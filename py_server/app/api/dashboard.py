"""
FastAPI router for dashboard operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models import InventoryItem, Alert, Priority
from app.services.notifications import get_dashboard_notifications, notification_manager

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    """Dashboard summary model."""
    total_items: int
    total_value: float
    low_stock_items: int
    out_of_stock_items: int
    pending_orders: int
    recent_alerts: int
    health_score: int
    last_updated: datetime


class CategoryStats(BaseModel):
    """Category statistics model."""
    category: str
    items_count: int
    total_value: float
    low_stock_count: int
    avg_stock_level: float
    top_items: List[Dict[str, Any]]


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    """
    Get dashboard summary with key metrics.
    """
    from app.services.database import db_manager
    
    try:
        # Get analytics from database
        analytics = await db_manager.get_inventory_analytics()
        
        # Get recent alerts count
        recent_alerts = await db_manager.get_alerts(limit=100, resolved=False)
        
        # Calculate health score based on stock levels
        total_items = analytics.get('total_items', 0)
        low_stock_count = analytics.get('low_stock_count', 0)
        out_of_stock_count = analytics.get('out_of_stock_count', 0)
        
        health_score = 100
        if total_items > 0:
            health_score = max(0, 100 - (low_stock_count * 5) - (out_of_stock_count * 10))
        
        return DashboardSummary(
            total_items=total_items,
            total_value=float(analytics.get('total_value', 0)),
            low_stock_items=low_stock_count,
            out_of_stock_items=out_of_stock_count,
            pending_orders=len([d for d in await db_manager.get_agent_decisions(limit=50) if not d.approved]),
            recent_alerts=len(recent_alerts),
            health_score=int(health_score),
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.get("/notifications")
async def get_dashboard_notifications_api(
    count: int = Query(20, ge=1, le=100),
    priority: Optional[Priority] = None
):
    """
    Get recent notifications for dashboard.
    """
    notifications = get_dashboard_notifications(count)
    
    if priority:
        notifications = [n for n in notifications if n.get('priority') == priority.value]
    
    return {
        "notifications": notifications,
        "total_count": len(notifications),
        "unread_count": len([n for n in notifications if n.get('read_at') is None])
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """
    Mark a notification as read.
    """
    notification_manager.mark_as_read(notification_id)
    return {"success": True, "message": "Notification marked as read"}


@router.get("/notifications/stats")
async def get_notification_stats():
    """
    Get notification statistics.
    """
    return notification_manager.get_notification_stats()


@router.get("/categories", response_model=List[CategoryStats])
async def get_category_statistics():
    """
    Get statistics by stationery category.
    """
    from app.services.database import db_manager
    from app.agents.stationery_agent import StationeryInventoryAgent
    
    try:
        # Get all inventory items
        items = await db_manager.get_inventory_items(limit=1000)
        
        if not items:
            return []
        
        # Group by category
        agent = StationeryInventoryAgent()
        category_data = {}
        
        for item in items:
            category = agent.categorize_stationery_item(item)
            category_name = category.value.replace('_', ' ').title()
            
            if category_name not in category_data:
                category_data[category_name] = {
                    'items': [],
                    'total_value': 0,
                    'low_stock_count': 0,
                    'stock_levels': []
                }
            
            item_value = item.current_stock * item.unit_cost
            category_data[category_name]['items'].append(item)
            category_data[category_name]['total_value'] += item_value
            category_data[category_name]['stock_levels'].append(item.current_stock)
            
            if item.current_stock <= item.min_stock_threshold:
                category_data[category_name]['low_stock_count'] += 1
        
        # Build response
        categories = []
        for category_name, data in category_data.items():
            # Get top items by value
            top_items = sorted(data['items'], key=lambda x: x.current_stock * x.unit_cost, reverse=True)[:5]
            top_items_data = [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "stock": item.current_stock,
                    "value": item.current_stock * item.unit_cost
                }
                for item in top_items
            ]
            
            avg_stock = sum(data['stock_levels']) / len(data['stock_levels']) if data['stock_levels'] else 0
            
            categories.append(CategoryStats(
                category=category_name,
                items_count=len(data['items']),
                total_value=data['total_value'],
                low_stock_count=data['low_stock_count'],
                avg_stock_level=round(avg_stock, 1),
                top_items=top_items_data
            ))
        
        return sorted(categories, key=lambda x: x.total_value, reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category statistics: {str(e)}")


@router.get("/trends")
async def get_inventory_trends():
    """
    Get inventory trends and analytics.
    """
    # Mock trend data
    current_date = datetime.now()
    trend_data = []
    
    for i in range(30):
        date = current_date - timedelta(days=i)
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "total_value": 25000 + (i * 100),
            "stock_level": 85 - (i * 0.5),
            "orders_placed": 2 + (i % 3),
            "alerts_generated": 1 + (i % 4)
        })
    
    trend_data.reverse()
    
    return {
        "daily_trends": trend_data,
        "summary": {
            "avg_stock_level": 82.5,
            "total_orders_30d": 45,
            "avg_daily_alerts": 2.1,
            "inventory_growth": 3.2
        }
    }


@router.get("/alerts", response_model=List[Alert])
async def get_recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    priority: Optional[Priority] = None,
    resolved: Optional[bool] = None
):
    """
    Get recent inventory alerts.
    """
    from app.services.database import db_manager
    
    try:
        alerts = await db_manager.get_alerts(limit=limit, resolved=resolved)
        
        if priority:
            alerts = [alert for alert in alerts if alert.priority == priority]
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.get("/seasonal-calendar")
async def get_seasonal_calendar():
    """
    Get educational calendar with seasonal events.
    """
    current_year = datetime.now().year
    
    educational_events = [
        {
            "date": f"{current_year}-03-01",
            "event": "Exam Preparation Season",
            "category": "writing_instruments",
            "impact": "high",
            "description": "Increased demand for pens, pencils, and writing materials"
        },
        {
            "date": f"{current_year}-04-15",
            "event": "School Preparation Begins",
            "category": "educational_books",
            "impact": "critical",
            "description": "Peak demand for textbooks and educational materials"
        },
        {
            "date": f"{current_year}-06-01",
            "event": "School Opening Rush",
            "category": "all_categories",
            "impact": "critical",
            "description": "Maximum demand across all stationery categories"
        },
        {
            "date": f"{current_year}-09-15",
            "event": "Mid-Session Restocking",
            "category": "paper_products",
            "impact": "medium",
            "description": "Regular restocking for paper products and consumables"
        },
        {
            "date": f"{current_year}-11-01",
            "event": "Exam Season",
            "category": "writing_instruments",
            "impact": "high",
            "description": "High demand for exam essentials and writing materials"
        }
    ]
    
    return {
        "events": educational_events,
        "current_season": "Regular Academic Period",
        "next_major_event": "School Opening Rush (June 2025)",
        "preparation_days": 45
    }


@router.get("/performance-metrics")
async def get_performance_metrics():
    """
    Get inventory performance metrics.
    """
    return {
        "inventory_turnover": 6.2,
        "stockout_rate": 2.1,
        "fill_rate": 97.9,
        "carrying_cost": 15.5,
        "order_accuracy": 98.7,
        "supplier_performance": {
            "on_time_delivery": 94.2,
            "quality_rating": 4.6,
            "cost_efficiency": 87.3
        },
        "ai_agent_performance": {
            "prediction_accuracy": 89.5,
            "cost_savings": 12.8,
            "automation_rate": 76.3,
            "user_satisfaction": 4.4
        }
    }


@router.get("/quick-actions")
async def get_quick_actions():
    """
    Get suggested quick actions for the dashboard.
    """
    return {
        "urgent_actions": [
            {
                "id": "restock_pens",
                "title": "Restock Blue Pens",
                "description": "Critical stock level for PEN001",
                "priority": "critical",
                "estimated_time": "2 hours"
            },
            {
                "id": "approve_orders",
                "title": "Approve Pending Orders",
                "description": "3 orders waiting for approval",
                "priority": "high",
                "estimated_time": "15 minutes"
            }
        ],
        "optimization_opportunities": [
            {
                "id": "bulk_negotiation",
                "title": "Bulk Order Negotiation",
                "description": "Potential 10% savings on paper products",
                "potential_savings": 1250.0,
                "estimated_time": "1 day"
            },
            {
                "id": "seasonal_prep",
                "title": "Seasonal Preparation",
                "description": "Prepare for upcoming school season",
                "potential_impact": "high",
                "estimated_time": "1 week"
            }
        ],
        "maintenance_tasks": [
            {
                "id": "update_patterns",
                "title": "Update Seasonal Patterns",
                "description": "Review and update AI learning patterns",
                "frequency": "monthly",
                "last_updated": "2024-11-15"
            }
        ]
    }