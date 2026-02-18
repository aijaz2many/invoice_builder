from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import fitz # PyMuPDF
from .. import schemas, models, deps
from ..core import database
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io

router = APIRouter(prefix="/pdf", tags=["PDF"])

# Ensure temp directory exists for generated PDFs
TEMP_DIR = "app/storage/temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

TEMPLATE_PATH = "app/storage/1/receipt_fields.pdf"

@router.post("/generate-invoice")
async def generate_invoice_pdf(
    data: schemas.InvoicePDFData, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Database Operations
    # Verify business exists
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == data.businessId))
    if not business_result.scalars().first():
        raise HTTPException(status_code=404, detail="Business not found")

    # Handle Customer (Find or Create)
    customer_query = await db.execute(
        select(models.Customer).where(
            models.Customer.businessId == data.businessId,
            models.Customer.customerName == data.CustomerName,
            models.Customer.customerPhone == data.customerPhone
        )
    )
    customer = customer_query.scalars().first()

    if not customer:
        customer = models.Customer(
            businessId=data.businessId,
            customerName=data.CustomerName,
            customerPhone=data.customerPhone,
            customerFullAddress=data.customerFullAddress
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)

    # Save Invoice
    new_invoice = models.Invoice(
        businessId=data.businessId,
        customerId=customer.customerId,
        invoiceNumber=data.invoiceNumber,
        BookNo=data.BookNo,
        invoiceAmount=data.invoiceAmount,
        amountInWords=data.amountinwords,
        paymentMode=data.paymentMode,
        paymentType=data.paymentType,
        purpose=data.purpose,
        billCollector=data.billCollector,
        Nazim=data.Nazim,
        pdfURL=f"/storage/temp/invoice_{data.invoiceNumber}.pdf" # Setting local path as URL for now
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)

    # 2. PDF Generation
    if not os.path.exists(TEMPLATE_PATH):
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        doc = fitz.open(TEMPLATE_PATH)
        page = doc.load_page(0)
        
        # Map pydantic data to a dictionary
        raw_data = data.model_dump()
        
        # Fill form fields by inserting text at widget locations and then deleting widgets
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name in raw_data and raw_data[field_name] is not None:
                text_value = str(raw_data[field_name])
                
                # Get widget properties
                rect = widget.rect
                
                # Insert text directly onto the page at the widget's location
                # Point(x, y) where y is the baseline of the text
                point = (rect.x0, rect.y1 - 3)
                
                page.insert_text(
                    point, 
                    text_value, 
                    fontname="hebo", # Helvetica Bold
                    fontsize=12,
                    color=(0, 0, 0) # Black text
                )
            
            # Delete the widget so the box is gone
            page.delete_widget(widget)
        
        # Ensure temp directory exists
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
        output_filename = f"invoice_{data.invoiceNumber}.pdf"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        # Save the modified PDF
        doc.save(output_path)
        doc.close()
            
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=output_filename
        )
        
    except Exception as e:
        import traceback
        print(f"PDF Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
