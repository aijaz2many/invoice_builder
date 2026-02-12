from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=schemas.RoleResponse)
async def create_role(role: schemas.RoleCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    # Check if role exists
    result = await db.execute(select(models.Role).where(models.Role.roleName == role.roleName))
    existing_role = result.scalars().first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    new_role = models.Role(roleName=role.roleName)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role

@router.get("/", response_model=List[schemas.RoleResponse])
async def read_roles(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Role).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{role_id}", response_model=schemas.RoleResponse)
async def read_role(role_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Role).where(models.Role.roleId == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Role).where(models.Role.roleId == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await db.delete(role)
    await db.commit()
    return {"message": "Role deleted"}
