from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from .. import models, deps
from ..core.database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Check if user is admin
    is_admin = any(role.roleName.lower() == 'admin' for role in current_user.roles)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Counts
    business_count = await db.scalar(select(func.count(models.Business.businessId)))
    invoice_count = await db.scalar(select(func.count(models.Invoice.invoiceId)))
    pending_templates = await db.scalar(select(func.count(models.Business.businessId)).where(models.Business.templateStatus == 'PENDING'))
    missing_templates = await db.scalar(select(func.count(models.Business.businessId)).where(models.Business.templateStatus == 'MISSING'))
    active_templates = await db.scalar(select(func.count(models.Business.businessId)).where(models.Business.templateStatus == 'ACTIVE'))
    user_count = await db.scalar(select(func.count(models.User.userId)))

    # Chart Data: Invoices over last 7 days
    today = datetime.now()
    seven_days_ago = today - timedelta(days=6)
    
    invoice_stats_query = select(
        func.date(models.Invoice.invoiceDate).label('date'),
        func.count(models.Invoice.invoiceId).label('count')
    ).where(
        models.Invoice.invoiceDate >= seven_days_ago
    ).group_by(
        func.date(models.Invoice.invoiceDate)
    ).order_by(
        func.date(models.Invoice.invoiceDate)
    )
    
    invoice_stats_result = await db.execute(invoice_stats_query)
    invoice_stats = invoice_stats_result.all()

    # Fill in missing days with zero
    invoice_chart_data = []
    for i in range(7):
        date = (seven_days_ago + timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        count = next((row.count for row in invoice_stats if str(row.date) == date_str), 0)
        invoice_chart_data.append({"date": date_str, "count": count})

    return {
        "businesses": business_count,
        "invoices": invoice_count,
        "pendingTemplates": pending_templates,
        "missingTemplates": missing_templates,
        "users": user_count,
        "charts": {
            "invoiceTimeline": invoice_chart_data,
            "templateDistribution": [
                {"label": "Active", "value": active_templates},
                {"label": "Pending", "value": pending_templates},
                {"label": "Missing", "value": missing_templates}
            ]
        }
    }
