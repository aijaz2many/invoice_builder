from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import schemas, models, deps
from ..core.database import get_db

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=schemas.InvoiceResponse)
async def create_invoice(
    invoice_data: schemas.InvoiceWithCustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Check if business exists
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == invoice_data.businessId))
    if not business_result.scalars().first():
        raise HTTPException(status_code=404, detail="Business not found")
    
    # 1. Handle Customer (Find or Create)
    # We check if a customer with the same name and phone exists for this business
    customer_query = await db.execute(
        select(models.Customer).where(
            models.Customer.businessId == invoice_data.businessId,
            models.Customer.customerName == invoice_data.customerName,
            models.Customer.customerPhone == invoice_data.customerPhone
        )
    )
    customer = customer_query.scalars().first()
    
    if not customer:
        # Create new customer
        customer = models.Customer(
            businessId=invoice_data.businessId,
            customerName=invoice_data.customerName,
            customerPhone=invoice_data.customerPhone,
            customerFullAddress=invoice_data.customerFullAddress
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
    
    # 2. Create Invoice
    new_invoice = models.Invoice(
        businessId=invoice_data.businessId,
        customerId=customer.customerId,
        invoiceNumber=invoice_data.invoiceNumber,
        invoiceAmount=invoice_data.invoiceAmount,
        amountInWords=invoice_data.amountInWords,
        paymentMode=invoice_data.paymentMode,
        paymentType=invoice_data.paymentType,
        purpose=invoice_data.purpose,
        pdfURL=invoice_data.pdfURL
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    return new_invoice

@router.get("/", response_model=List[schemas.InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Invoice).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Invoice).where(models.Invoice.invoiceId == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.get("/business/{business_id}", response_model=List[schemas.InvoiceResponse])
async def get_business_invoices(
    business_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Invoice).where(models.Invoice.businessId == business_id))
    return result.scalars().all()

@router.put("/{invoice_id}", response_model=schemas.InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: schemas.InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Invoice).where(models.Invoice.invoiceId == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    for key, value in invoice_update.model_dump().items():
        setattr(invoice, key, value)
    
    await db.commit()
    await db.refresh(invoice)
    return invoice

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    result = await db.execute(select(models.Invoice).where(models.Invoice.invoiceId == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    await db.delete(invoice)
    await db.commit()
    return {"message": "Invoice deleted"}
