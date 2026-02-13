from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=schemas.CustomerResponse)
async def create_customer(
    customer: schemas.CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Check if business exists
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == customer.businessId))
    if not business_result.scalars().first():
        raise HTTPException(status_code=404, detail="Business not found")
    
    new_customer = models.Customer(**customer.model_dump())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

@router.get("/", response_model=List[schemas.CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Customer).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
async def get_customer(
    customer_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Customer).where(models.Customer.customerId == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/business/{business_id}", response_model=List[schemas.CustomerResponse])
async def get_business_customers(
    business_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Customer).where(models.Customer.businessId == business_id))
    return result.scalars().all()

@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: schemas.CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Customer).where(models.Customer.customerId == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer_update.model_dump().items():
        setattr(customer, key, value)
    
    await db.commit()
    await db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Customer).where(models.Customer.customerId == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await db.delete(customer)
    await db.commit()
    return {"message": "Customer deleted"}
