from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.post("/", response_model=schemas.BusinessResponse)
async def create_business(
    business: schemas.BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Check if business name exists
    result = await db.execute(select(models.Business).where(models.Business.businessName == business.businessName))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Business name already exists")
    
    # Check if business type exists
    bt_result = await db.execute(select(models.BusinessType).where(models.BusinessType.businessTypeId == business.businessTypeId))
    if not bt_result.scalars().first():
        raise HTTPException(status_code=400, detail="Invalid business type")
    
    new_business = models.Business(**business.model_dump())
    db.add(new_business)
    await db.commit()
    await db.refresh(new_business)
    return new_business

@router.get("/", response_model=List[schemas.BusinessResponse])
async def list_businesses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Business).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{business_id}", response_model=schemas.BusinessResponse)
async def get_business(business_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Business).where(models.Business.businessId == business_id))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get("/user/{user_id}", response_model=List[schemas.BusinessResponse])
async def get_user_businesses(user_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Business).where(models.Business.userId == user_id))
    return result.scalars().all()

@router.put("/{business_id}", response_model=schemas.BusinessResponse)
async def update_business(
    business_id: int,
    business_update: schemas.BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Business).where(models.Business.businessId == business_id))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions (only owner can update)
    if business.userId != current_user.userId:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    for key, value in business_update.model_dump().items():
        setattr(business, key, value)
    
    await db.commit()
    await db.refresh(business)
    return business

@router.delete("/{business_id}")
async def delete_business(
    business_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Business).where(models.Business.businessId == business_id))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business.userId != current_user.userId:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    business.isActive = False
    await db.commit()
    return {"message": "Business deactivated"}
