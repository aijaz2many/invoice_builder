from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import schemas, models, deps
from ..core import database, security, config
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(prefix="/auth")

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    # Check if user exists
    result = await db.execute(select(models.User).where(models.User.emailId == user.emailId))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    # Ensure phone_number is provided if required by DB which is nullable=False
    if not user.phoneNumber:
         raise HTTPException(status_code=400, detail="Phone number is required")

    new_user = models.User(
        emailId=user.emailId,
        hashPassword=hashed_password,
        fullName=user.fullName,
        phoneNumber=user.phoneNumber,
        algoPassword="bcrypt"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Assign Default User Role
    # Find or create 'user' role
    role_result = await db.execute(select(models.Role).where(models.Role.roleName == "user"))
    default_role = role_result.scalars().first()
    
    if not default_role:
        default_role = models.Role(roleName="user")
        db.add(default_role)
        await db.commit()
        await db.refresh(default_role)
    
    # Create UserRole entry
    user_role = models.UserRole(userId=new_user.userId, roleId=default_role.roleId)
    db.add(user_role)
    await db.commit()

    return new_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).where(models.User.emailId == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.hashPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Force password change if default
    if form_data.password == "12345678":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Default password detected. please use /auth/reset-password to change it."
        )

    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.emailId}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(request: schemas.ForgotPassword, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).where(models.User.emailId == request.emailId))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Reset to default password
    user.hashPassword = security.get_password_hash("12345678")
    db.add(user)
    await db.commit()
    return {"message": "Password has been reset to default '12345678'. Please change it on next login."}

@router.post("/reset-password")
async def reset_password(request: schemas.ResetPassword, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).where(models.User.emailId == request.emailId))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not security.verify_password(request.currentPassword, user.hashPassword):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    if request.newPassword == "12345678":
        raise HTTPException(status_code=400, detail="New password cannot be the default password")
        
    user.hashPassword = security.get_password_hash(request.newPassword)
    db.add(user)
    await db.commit()
    return {"message": "Password changed successfully"}
