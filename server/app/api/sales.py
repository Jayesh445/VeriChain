from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.services.database import SalesService
from app.core.logging import logger

router = APIRouter()


@router.get("/analytics")
async def get_sales_analytics(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive sales analytics for dashboard"""
    try:
        trends = await SalesService.get_sales_trends(db, days=days)
        top_items = await SalesService.get_top_selling_items(db, limit=10, days=days)
        
        # Calculate additional analytics
        total_sales = sum(item.get('quantity', 0) for item in trends) if trends else 0
        revenue = sum(item.get('revenue', 0) for item in trends) if trends else 0
        avg_daily_sales = total_sales / days if days > 0 else 0
        
        return {
            "success": True,
            "analytics": {
                "total_sales": total_sales,
                "total_revenue": revenue,
                "average_daily_sales": avg_daily_sales,
                "daily_trends": trends or [],
                "top_selling_items": top_items or [],
                "period_days": days,
                "growth_rate": 5.2  # placeholder for now
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sales analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales analytics: {str(e)}"
        )