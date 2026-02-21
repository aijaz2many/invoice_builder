from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
import os
import fitz # PyMuPDF
import httpx
from .. import schemas, models, deps
from ..core import database
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io
from typing import List

router = APIRouter(prefix="/pdf", tags=["PDF"])

OCI_PAR_URL = "https://objectstorage.ap-mumbai-1.oraclecloud.com/p/IBDUyhhzwHNkcqt2_NvHqebRPyaN2tVfZuaqKpilDa0foleXa2TAU2xaiukX3NTB/n/bm3luqkdqbty/b/testing/o/"

@router.post("/upload-template/{businessId}")
async def upload_template(
    businessId: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Verify business exists
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == businessId))
    business = business_result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    file_ext = file.filename.split('.')[-1].lower()
    is_pdf = file_ext == 'pdf'
    is_image = file_ext in ['jpg', 'jpeg', 'png']

    if not is_pdf and not is_image:
        raise HTTPException(status_code=400, detail="Only PDF or Image (JPG, PNG) files are allowed")

    # 2. Upload to Oracle Object Storage
    try:
        file_content = await file.read()
        filename = "receipt_fields.pdf" if is_pdf else f"raw_template.{file_ext}"
        oci_upload_url = f"{OCI_PAR_URL}{businessId}/{filename}"
        
        async with httpx.AsyncClient() as client:
            response = await client.put(oci_upload_url, content=file_content)
            if response.status_code not in [200, 201]:
                print(f"OCI Upload Failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="Failed to upload to Cloud Storage")
        
        # 3. Update Business Status
        business.templateStatus = "ACTIVE" if is_pdf else "PENDING"
        await db.commit()

    except Exception as e:
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

    return {
        "message": "Template uploaded successfully", 
        "status": "success",
        "templateStatus": business.templateStatus
    }

@router.get("/template/{businessId}")
async def get_template(
    businessId: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Verify business exists and check status
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == businessId))
    business = business_result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.templateStatus == "MISSING":
        raise HTTPException(status_code=404, detail="No template has been uploaded for this business yet")

    # 2. Determine filename and media type based on status
    target_filename = "receipt_fields.pdf"
    media_type = "application/pdf"
    
    if business.templateStatus == "PENDING":
        # Try to find the raw image. We'll check common extensions.
        # Note: In a production environment, you might store the exact extension in the DB.
        found = False
        for ext in ["jpg", "jpeg", "png"]:
            oci_check_url = f"{OCI_PAR_URL}{businessId}/raw_template.{ext}"
            async with httpx.AsyncClient() as client:
                response = await client.get(oci_check_url)
                if response.status_code == 200:
                    target_filename = f"raw_template.{ext}"
                    media_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                    content = response.content
                    found = True
                    break
        if not found:
            raise HTTPException(status_code=404, detail="Pending template file not found on Cloud Storage")
    else:
        # ACTIVE status
        oci_download_url = f"{OCI_PAR_URL}{businessId}/{target_filename}"
        async with httpx.AsyncClient() as client:
            response = await client.get(oci_download_url)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Active template PDF not found on Cloud Storage")
            content = response.content

    # 3. Return the file
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename={target_filename}"
        }
    )

@router.post("/generate-invoice")
async def generate_invoice_pdf(
    data: schemas.InvoicePDFData, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # 1. Database Operations
    # Verify business exists
    business_result = await db.execute(select(models.Business).where(models.Business.businessId == data.businessId))
    business = business_result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check template status
    if business.templateStatus != "ACTIVE":
         raise HTTPException(status_code=400, detail="Business template is not active. Please wait for admin approval if you uploaded an image.")

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

    # Define cloud storage path for the generated invoice
    safe_date = data.invoiceDate.replace("/", "-").replace("\\", "-")
    invoice_filename = f"invoice_{data.invoiceNumber}_{safe_date}.pdf"
    cloud_invoice_url = f"{OCI_PAR_URL}{data.businessId}/invoices/{invoice_filename}"

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
        pdfURL=cloud_invoice_url
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)

    # 2. PDF Generation
    # Fetch template directly from OCI into memory
    try:
        oci_download_url = f"{OCI_PAR_URL}{data.businessId}/receipt_fields.pdf"
        async with httpx.AsyncClient() as client:
            response = await client.get(oci_download_url)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Template not found on Cloud Storage for business {data.businessId}")
            template_content = response.content
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error fetching template from Cloud: {str(e)}")
    
    try:
        # Open PDF from memory stream
        doc = fitz.open(stream=template_content, filetype="pdf")
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
        
        # Get the final PDF content in memory
        pdf_bytes = doc.write()
        doc.close()

        # 3. Upload generated invoice to Cloud Storage
        try:
            async with httpx.AsyncClient() as client:
                upload_response = await client.put(cloud_invoice_url, content=pdf_bytes)
                if upload_response.status_code not in [200, 201]:
                    print(f"Cloud Invoice Upload Failed: {upload_response.status_code} - {upload_response.text}")
        except Exception as e:
            print(f"Cloud Invoice Upload Error: {str(e)}")

        # Return the PDF directly from memory
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_filename}"
            }
        )
        
    except Exception as e:
        import traceback
        print(f"PDF Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
