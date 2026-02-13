from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/business-types", tags=["Business Types"])

@router.post("/", response_model=schemas.BusinessTypeResponse)
async def create_business_type(
    bt: schemas.BusinessTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.BusinessType).where(models.BusinessType.businessTypeName == bt.businessTypeName))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Business type already exists")
    
    new_bt = models.BusinessType(**bt.model_dump())
    db.add(new_bt)
    await db.commit()
    await db.refresh(new_bt)
    return new_bt

@router.get("/", response_model=List[schemas.BusinessTypeResponse])
async def list_business_types(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.BusinessType).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{bt_id}", response_model=schemas.BusinessTypeResponse)
async def get_business_type(bt_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.BusinessType).where(models.BusinessType.businessTypeId == bt_id))
    bt = result.scalars().first()
    if not bt:
        raise HTTPException(status_code=404, detail="Business type not found")
    return bt

@router.put("/{bt_id}", response_model=schemas.BusinessTypeResponse)
async def update_business_type(
    bt_id: int,
    bt_update: schemas.BusinessTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.BusinessType).where(models.BusinessType.businessTypeId == bt_id))
    bt = result.scalars().first()
    if not bt:
        raise HTTPException(status_code=404, detail="Business type not found")
    
    for key, value in bt_update.model_dump().items():
        setattr(bt, key, value)
    
    await db.commit()
    await db.refresh(bt)
    return bt

@router.delete("/{bt_id}")
async def delete_business_type(
    bt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.BusinessType).where(models.BusinessType.businessTypeId == bt_id))
    bt = result.scalars().first()
    if not bt:
        raise HTTPException(status_code=404, detail="Business type not found")
    
    bt.isActive = False
    await db.commit()
    return {"message": "Business type deactivated"}
