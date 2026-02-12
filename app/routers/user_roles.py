from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/user-roles", tags=["User Roles"])

@router.post("/", response_model=schemas.UserRoleResponse)
async def assign_role_to_user(
    user_role: schemas.UserRoleBase, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    # Check if user exists
    user_result = await db.execute(select(models.User).where(models.User.userId == user_role.userId))
    if not user_result.scalars().first():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if role exists
    role_result = await db.execute(select(models.Role).where(models.Role.roleId == user_role.roleId))
    if not role_result.scalars().first():
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if assignment already exists
    exists_result = await db.execute(
        select(models.UserRole).where(
            models.UserRole.userId == user_role.userId,
            models.UserRole.roleId == user_role.roleId
        )
    )
    if exists_result.scalars().first():
        raise HTTPException(status_code=400, detail="User already has this role")
    
    new_user_role = models.UserRole(userId=user_role.userId, roleId=user_role.roleId)
    db.add(new_user_role)
    await db.commit()
    await db.refresh(new_user_role)
    return new_user_role

@router.get("/", response_model=List[schemas.UserRoleResponse])
async def list_user_roles(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.UserRole).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/user/{user_id}", response_model=List[schemas.UserRoleResponse])
async def get_roles_for_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.UserRole).where(models.UserRole.userId == user_id))
    return result.scalars().all()

@router.delete("/{user_role_id}")
async def remove_role_from_user(
    user_role_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.UserRole).where(models.UserRole.userRoleId == user_role_id))
    ur = result.scalars().first()
    if not ur:
        raise HTTPException(status_code=404, detail="UserRole assignment not found")
    
    await db.delete(ur)
    await db.commit()
    return {"message": "Role removed from user"}
