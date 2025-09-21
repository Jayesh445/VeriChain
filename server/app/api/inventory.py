from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import select, update

from app.core.database import get_db
from app.models import (
    StationeryItem, SalesRecord,
    StationeryItemResponse, StationeryItemCreate, StationeryItemUpdate,
    SalesRecordResponse, SalesRecordCreate, InventoryAlert
)
from app.core.logging import logger


class StockUpdateRequest(BaseModel):
    quantity: int
    reason: str = "Manual adjustment"
    updated_by: str = "admin"


class InventoryService:
    @staticmethod
    async def get_all_items(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(StationeryItem).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get_item_by_id(db: AsyncSession, item_id: int):
        result = await db.execute(select(StationeryItem).where(StationeryItem.id == item_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_low_stock_items(db: AsyncSession):
        result = await db.execute(
            select(StationeryItem).where(StationeryItem.current_stock <= StationeryItem.reorder_level)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_out_of_stock_items(db: AsyncSession):
        result = await db.execute(select(StationeryItem).where(StationeryItem.current_stock == 0))
        return result.scalars().all()
    
    @staticmethod
    async def get_overstock_items(db: AsyncSession):
        result = await db.execute(
            select(StationeryItem).where(StationeryItem.current_stock > StationeryItem.max_stock_level)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_inventory_summary(db: AsyncSession):
        # Get total items
        total_result = await db.execute(select(StationeryItem))
        total_items = len(total_result.scalars().all())
        
        # Get low stock count
        low_stock_result = await db.execute(
            select(StationeryItem).where(StationeryItem.current_stock <= StationeryItem.reorder_level)
        )
        low_stock_count = len(low_stock_result.scalars().all())
        
        # Get out of stock count
        out_stock_result = await db.execute(select(StationeryItem).where(StationeryItem.current_stock == 0))
        out_of_stock_count = len(out_stock_result.scalars().all())
        
        return {
            "total_items": total_items,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "healthy_stock_items": total_items - low_stock_count - out_of_stock_count
        }


class SalesService:
    @staticmethod
    async def get_sales_by_period(db: AsyncSession, start_date: datetime, end_date: datetime, item_id: Optional[int] = None):
        query = select(SalesRecord).where(
            SalesRecord.sale_date >= start_date,
            SalesRecord.sale_date <= end_date
        )
        if item_id:
            query = query.where(SalesRecord.item_id == item_id)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_sales_trends(db: AsyncSession, days: int = 30):
        # Simple implementation - return placeholder data
        return []
    
    @staticmethod
    async def get_top_selling_items(db: AsyncSession, limit: int = 10, days: int = 30):
        # Simple implementation - return placeholder data
        return []
    
    @staticmethod
    async def create_sale(db: AsyncSession, sale_data: dict):
        # Create a new sale record
        sale = SalesRecord(**sale_data)
        db.add(sale)
        await db.commit()
        await db.refresh(sale)
        return sale
    
    @staticmethod
    async def detect_sales_anomalies(db: AsyncSession, item_id: int):
        # Simple implementation - return placeholder data
        return []

router = APIRouter()


@router.get("/items")
async def get_inventory_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get inventory items with optional filtering"""
    try:
        if low_stock_only:
            items = await InventoryService.get_low_stock_items(db)
        else:
            items = await InventoryService.get_all_items(db, skip=skip, limit=limit)
        
        # Convert to dict format to avoid enum issues
        result = []
        for item in items:
            item_data = {
                "id": item.id,
                "sku": item.sku,
                "name": item.name,
                "category": str(item.category).replace("ItemCategory.", ""),
                "brand": item.brand,
                "unit": item.unit,
                "unit_cost": item.unit_cost,
                "current_stock": item.current_stock,
                "reorder_level": item.reorder_level,
                "max_stock_level": item.max_stock_level,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            }
            # Filter by category if specified
            if not category or str(item.category).upper() == category.upper():
                result.append(item_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get inventory items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory items: {str(e)}"
        )


@router.get("/items/{item_id}", response_model=StationeryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific inventory item"""
    try:
        item = await InventoryService.get_item_by_id(db, item_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get inventory item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory item: {str(e)}"
        )


@router.get("/summary")
async def get_inventory_summary(db: AsyncSession = Depends(get_db)):
    """Get inventory summary statistics"""
    try:
        summary = await InventoryService.get_inventory_summary(db)
        
        # Get additional details
        low_stock_items = await InventoryService.get_low_stock_items(db)
        out_of_stock_items = await InventoryService.get_out_of_stock_items(db)
        overstock_items = await InventoryService.get_overstock_items(db)
        
        return {
            "success": True,
            "summary": summary,
            "details": {
                "low_stock_items": [
                    {
                        "id": item.id,
                        "sku": item.sku,
                        "name": item.name,
                        "current_stock": item.current_stock,
                        "reorder_level": item.reorder_level,
                        "category": item.category.value
                    }
                    for item in low_stock_items[:10]  # Limit to 10 for performance
                ],
                "out_of_stock_items": [
                    {
                        "id": item.id,
                        "sku": item.sku,
                        "name": item.name,
                        "category": item.category.value
                    }
                    for item in out_of_stock_items[:10]
                ],
                "overstock_items": [
                    {
                        "id": item.id,
                        "sku": item.sku,
                        "name": item.name,
                        "current_stock": item.current_stock,
                        "max_stock_level": item.max_stock_level,
                        "category": item.category.value
                    }
                    for item in overstock_items[:10]
                ]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get inventory summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory summary: {str(e)}"
        )


@router.get("/alerts")
async def get_inventory_alerts(db: AsyncSession = Depends(get_db)):
    """Get current inventory alerts"""
    try:
        alerts = []
        
        # Get low stock items
        low_stock_items = await InventoryService.get_low_stock_items(db)
        for item in low_stock_items:
            severity = "critical" if item.current_stock <= 0 else "high"
            alert_type = "out_of_stock" if item.current_stock <= 0 else "low_stock"
            
            alerts.append(InventoryAlert(
                item_id=item.id,
                sku=item.sku,
                name=item.name,
                current_stock=item.current_stock,
                reorder_level=item.reorder_level,
                alert_type=alert_type,
                severity=severity
            ))
        
        # Get overstock items
        overstock_items = await InventoryService.get_overstock_items(db)
        for item in overstock_items:
            alerts.append(InventoryAlert(
                item_id=item.id,
                sku=item.sku,
                name=item.name,
                current_stock=item.current_stock,
                reorder_level=item.reorder_level,
                alert_type="overstock",
                severity="medium"
            ))
        
        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get inventory alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory alerts: {str(e)}"
        )


@router.post("/items/{item_id}/stock/update")
async def update_item_stock(
    item_id: int,
    request: StockUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update stock level for an item and trigger AI negotiation if needed"""
    try:
        # Get the item first
        result = await db.execute(select(StationeryItem).where(StationeryItem.id == item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )
        
        # Update the stock
        old_stock = item.current_stock
        new_stock = item.current_stock + request.quantity
        if new_stock < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reduce stock by {abs(request.quantity)}. Current stock: {item.current_stock}"
            )
        
        # Update the item
        await db.execute(
            update(StationeryItem)
            .where(StationeryItem.id == item_id)
            .values(
                current_stock=new_stock,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        # Refresh the item to get updated values
        await db.refresh(item)
        
        # Check if stock reduction triggered reorder condition and auto-start negotiation
        negotiation_triggered = False
        if (request.quantity < 0 and  # Stock was reduced
            new_stock <= item.reorder_level and  # Below reorder level
            old_stock > item.reorder_level):  # Previously above reorder level
            
            try:
                # Import here to avoid circular dependency
                from app.api.ai_agent import start_negotiation_background
                
                # Calculate recommended quantity (bring back to max level)
                recommended_quantity = max(item.max_stock_level - new_stock, item.reorder_level)
                
                # Start AI negotiation process
                negotiation_data = {
                    "item_id": item_id,
                    "quantity_needed": recommended_quantity,
                    "urgency": "high" if new_stock == 0 else "medium",
                    "trigger_source": "stock_reduction",
                    "reduction_context": {
                        "old_stock": old_stock,
                        "new_stock": new_stock,
                        "reduction_amount": abs(request.quantity),
                        "reason": request.reason,
                        "updated_by": request.updated_by
                    }
                }
                
                session_id = await start_negotiation_background(db, negotiation_data)
                negotiation_triggered = True
                
                logger.info(f"Auto-started negotiation {session_id} for item {item_id} due to stock reduction")
                
            except Exception as e:
                logger.error(f"Failed to start auto-negotiation: {str(e)}")
                # Don't fail the stock update if negotiation fails
        
        response = {
            "success": True,
            "message": f"Stock updated by {request.quantity} units",
            "item_id": item_id,
            "old_stock_level": old_stock,
            "new_stock_level": new_stock,
            "reason": request.reason,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add negotiation info if triggered
        if negotiation_triggered:
            response["auto_negotiation"] = {
                "triggered": True,
                "session_id": session_id,
                "message": f"AI negotiation started automatically for {item.name} due to low stock"
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update stock: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update stock: {str(e)}"
        )


@router.get("/sales/recent")
async def get_recent_sales(
    days: int = Query(7, ge=1, le=90),
    item_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent sales data"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sales = await SalesService.get_sales_by_period(
            db=db,
            start_date=start_date,
            end_date=end_date,
            item_id=item_id
        )
        
        return {
            "success": True,
            "sales": [
                {
                    "id": sale.id,
                    "item_id": sale.item_id,
                    "item_name": sale.item.name if sale.item else "Unknown",
                    "item_sku": sale.item.sku if sale.item else "Unknown",
                    "quantity_sold": sale.quantity_sold,
                    "unit_price": sale.unit_price,
                    "total_amount": sale.total_amount,
                    "department": sale.department,
                    "sale_date": sale.sale_date.isoformat()
                }
                for sale in sales
            ],
            "count": len(sales),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent sales: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent sales: {str(e)}"
        )


@router.get("/sales/analytics")
async def get_sales_analytics(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive sales analytics for dashboard"""
    try:
        trends = await SalesService.get_sales_trends(db, days=days)
        top_items = await SalesService.get_top_selling_items(db, limit=10, days=days)
        
        # Calculate additional analytics
        total_sales = sum(item.get('quantity', 0) for item in trends)
        revenue = sum(item.get('revenue', 0) for item in trends)
        avg_daily_sales = total_sales / days if days > 0 else 0
        
        return {
            "success": True,
            "analytics": {
                "total_sales": total_sales,
                "total_revenue": revenue,
                "average_daily_sales": avg_daily_sales,
                "daily_trends": trends,
                "top_selling_items": top_items,
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


@router.get("/sales/trends")
async def get_sales_trends(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get sales trends analysis"""
    try:
        trends = await SalesService.get_sales_trends(db, days=days)
        top_items = await SalesService.get_top_selling_items(db, limit=10, days=days)
        
        return {
            "success": True,
            "trends": {
                "daily_trends": trends,
                "top_selling_items": top_items,
                "period_days": days,
                "total_sales_days": len(trends)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sales trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales trends: {str(e)}"
        )


@router.post("/sales", response_model=SalesRecordResponse)
async def create_sale(
    sale_data: SalesRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new sales record"""
    try:
        # Verify item exists
        item = await InventoryService.get_item_by_id(db, sale_data.item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )
        
        # Check stock availability
        if item.current_stock < sale_data.quantity_sold:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {item.current_stock}, Requested: {sale_data.quantity_sold}"
            )
        
        # Create sale record
        sale = await SalesService.create_sale(db, sale_data.dict())
        
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create sale: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sale: {str(e)}"
        )


@router.get("/analytics/item/{item_id}")
async def get_item_analytics(
    item_id: int,
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for a specific item"""
    try:
        # Get item details
        item = await InventoryService.get_item_by_id(db, item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )
        
        # Get sales data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        sales = await SalesService.get_sales_by_period(
            db=db, start_date=start_date, end_date=end_date, item_id=item_id
        )
        
        # Get anomaly analysis
        anomalies = await SalesService.detect_sales_anomalies(db, item_id)
        
        # Calculate metrics
        total_sold = sum(sale.quantity_sold for sale in sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        avg_daily_sales = total_sold / days if days > 0 else 0
        
        return {
            "success": True,
            "item": {
                "id": item.id,
                "sku": item.sku,
                "name": item.name,
                "category": item.category.value,
                "current_stock": item.current_stock,
                "reorder_level": item.reorder_level,
                "max_stock_level": item.max_stock_level
            },
            "analytics": {
                "period_days": days,
                "total_sold": total_sold,
                "total_revenue": total_revenue,
                "avg_daily_sales": avg_daily_sales,
                "transaction_count": len(sales),
                "stock_days_remaining": item.current_stock / avg_daily_sales if avg_daily_sales > 0 else float('inf'),
                "anomalies": anomalies
            },
            "sales_history": [
                {
                    "quantity_sold": sale.quantity_sold,
                    "unit_price": sale.unit_price,
                    "total_amount": sale.total_amount,
                    "sale_date": sale.sale_date.isoformat(),
                    "department": sale.department
                }
                for sale in sales[-20:]  # Last 20 sales
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get item analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get item analytics: {str(e)}"
        )