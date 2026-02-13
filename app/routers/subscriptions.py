from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# --- Subscription Plans ---
@router.post("/plans", response_model=schemas.SubscriptionPlanResponse)
async def create_plan(plan: schemas.SubscriptionPlanCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    new_plan = models.SubscriptionPlan(**plan.model_dump())
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    return new_plan

@router.get("/plans", response_model=List[schemas.SubscriptionPlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubscriptionPlan).where(models.SubscriptionPlan.subscriptionPlanStatus == True))
    return result.scalars().all()

@router.put("/plans/{plan_id}", response_model=schemas.SubscriptionPlanResponse)
async def update_plan(
    plan_id: int, 
    plan_update: schemas.SubscriptionPlanUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.SubscriptionPlan).where(models.SubscriptionPlan.subscriptionPlanId == plan_id))
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    update_data = plan_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    
    await db.commit()
    await db.refresh(plan)
    return plan

# --- Subscriptions ---
@router.post("/", response_model=schemas.SubscriptionResponse)
async def create_subscription(sub: schemas.SubscriptionCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    # Verify business and plan exist
    bus = await db.execute(select(models.Business).where(models.Business.businessId == sub.businessId))
    if not bus.scalars().first():
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check if subscription already exists for this business
    existing_sub = await db.execute(select(models.Subscription).where(models.Subscription.businessId == sub.businessId))
    if existing_sub.scalars().first():
        raise HTTPException(status_code=400, detail="Subscription already exists for this business")
    
    plan = await db.execute(select(models.SubscriptionPlan).where(models.SubscriptionPlan.subscriptionPlanId == sub.subscriptionPlanId))
    if not plan.scalars().first():
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    new_sub = models.Subscription(**sub.model_dump())
    db.add(new_sub)
    await db.commit()
    await db.refresh(new_sub)
    return new_sub

@router.get("/business/{business_id}", response_model=List[schemas.SubscriptionResponse])
async def get_business_subscriptions(business_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.Subscription).where(models.Subscription.businessId == business_id))
    return result.scalars().all()

@router.put("/{sub_id}", response_model=schemas.SubscriptionResponse)
async def update_subscription(
    sub_id: int, 
    sub_update: schemas.SubscriptionUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Subscription).where(models.Subscription.subscriptionId == sub_id))
    sub = result.scalars().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_data = sub_update.model_dump(exclude_unset=True)
    
    # If updating planId, verify it exists
    if "subscriptionPlanId" in update_data:
        plan_check = await db.execute(select(models.SubscriptionPlan).where(models.SubscriptionPlan.subscriptionPlanId == update_data["subscriptionPlanId"]))
        if not plan_check.scalars().first():
            raise HTTPException(status_code=404, detail="New subscription plan not found")

    for key, value in update_data.items():
        setattr(sub, key, value)
    
    await db.commit()
    await db.refresh(sub)
    return sub

# --- Payments ---
@router.post("/payments", response_model=schemas.SubscriptionPaymentResponse)
async def create_payment(payment: schemas.SubscriptionPaymentCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    sub = await db.execute(select(models.Subscription).where(models.Subscription.subscriptionId == payment.subscriptionId))
    if not sub.scalars().first():
        raise HTTPException(status_code=404, detail="Subscription not found")

    new_payment = models.SubscriptionPayment(**payment.model_dump())
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment

@router.get("/payments/subscription/{subscription_id}", response_model=List[schemas.SubscriptionPaymentResponse])
async def list_payments(subscription_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.SubscriptionPayment).where(models.SubscriptionPayment.subscriptionId == subscription_id))
    return result.scalars().all()

@router.put("/payments/{payment_id}", response_model=schemas.SubscriptionPaymentResponse)
async def update_payment(
    payment_id: int, 
    payment_update: schemas.SubscriptionPaymentUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.SubscriptionPayment).where(models.SubscriptionPayment.subscriptionPaymentId == payment_id))
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Subscription payment record not found")
    
    update_data = payment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(payment, key, value)
    
    await db.commit()
    await db.refresh(payment)
    return payment

# --- Usage ---
@router.post("/usage", response_model=schemas.SubscriptionUsageResponse)
async def log_usage(usage: schemas.SubscriptionUsageCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    sub = await db.execute(select(models.Subscription).where(models.Subscription.subscriptionId == usage.subscriptionId))
    if not sub.scalars().first():
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Check if usage for this month already exists
    exists = await db.execute(
        select(models.SubscriptionUsage).where(
            models.SubscriptionUsage.subscriptionId == usage.subscriptionId,
            models.SubscriptionUsage.usageMonth == usage.usageMonth
        )
    )
    existing_usage = exists.scalars().first()
    if existing_usage:
        existing_usage.invoiceCount = usage.invoiceCount
        db.add(existing_usage)
    else:
        new_usage = models.SubscriptionUsage(**usage.model_dump())
        db.add(new_usage)
    
    await db.commit()
    if existing_usage:
        await db.refresh(existing_usage)
        return existing_usage
    else:
        await db.refresh(new_usage)
        return new_usage

@router.get("/usage/{subscription_id}", response_model=List[schemas.SubscriptionUsageResponse])
async def get_usage(subscription_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    result = await db.execute(select(models.SubscriptionUsage).where(models.SubscriptionUsage.subscriptionId == subscription_id))
    return result.scalars().all()

@router.put("/usage/{usage_id}", response_model=schemas.SubscriptionUsageResponse)
async def update_usage(
    usage_id: int, 
    usage_update: schemas.SubscriptionUsageUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.SubscriptionUsage).where(models.SubscriptionUsage.subscriptionUsageId == usage_id))
    usage = result.scalars().first()
    if not usage:
        raise HTTPException(status_code=404, detail="Subscription usage record not found")
    
    update_data = usage_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usage, key, value)
    
    await db.commit()
    await db.refresh(usage)
    return usage
