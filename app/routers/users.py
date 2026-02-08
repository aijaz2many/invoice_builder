from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .. import schemas, models, deps
from ..core.database import get_db
from ..core import security

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: int, current_user: models.User = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=schemas.UserResponse)
async def update_user(
    update_data: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.email is not None:
        # Check if email is taken by another user
        result = await db.execute(select(models.User).where(models.User.email == update_data.email))
        existing_user = result.scalars().first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = update_data.email
        
    if update_data.password is not None:
        current_user.hashed_password = security.get_password_hash(update_data.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.delete("/me", status_code=204)
async def delete_user(current_user: models.User = Depends(deps.get_current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(current_user)
    await db.commit()
    return

# Admin route example (logic only)
@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(deps.get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # In a real app, check if current_user is admin
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users
