"""
FastAPI router for dashboard operations with AI-powered insights.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from app.models.database import InventoryItemDB, SalesDataDB, AgentDecisionDB
from app.services.database import DatabaseManager
from app.services.ai_service import get_ai_service
from app.services.negotiation_chat import negotiation_manager
from app.services.notifications_enhanced import notification_manager

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    """Dashboard summary model with AI insights."""
    total_items: int
    total_value: float
    low_stock_items: int
    out_of_stock_items: int
    pending_orders: int
    recent_alerts: int
    health_score: int
    last_updated: datetime
    ai_insights: Dict[str, Any]
    recommendations: List[str]


class CategoryStats(BaseModel):
    """Category statistics model with AI analysis."""
    category: str
    items_count: int
    total_value: float
    low_stock_count: int
    avg_stock_level: float
    top_items: List[Dict[str, Any]]
    ai_analysis: Dict[str, Any]
    trend_prediction: str


class SalesAnalytics(BaseModel):
    """Sales analytics with AI predictions."""
    total_sales: float
    sales_count: int
    avg_order_value: float
    top_selling_items: List[Dict[str, Any]]
    sales_trend: str
    period_comparison: Dict[str, Any]
    ai_forecast: Dict[str, Any]


class InventoryOverview(BaseModel):
    """Inventory overview with AI optimization."""
    total_items: int
    categories: List[str]
    stock_distribution: Dict[str, int]
    critical_items: List[Dict[str, Any]]
    optimization_suggestions: List[str]
    ai_health_score: float


class NegotiationSummary(BaseModel):
    """Negotiation summary with AI insights."""
    active_negotiations: int
    completed_negotiations: int
    success_rate: float
    average_savings: float
    top_suppliers: List[Dict[str, Any]]
    ai_negotiation_insights: Dict[str, Any]


class DashboardInsights(BaseModel):
    """AI-powered dashboard insights."""
    insight_type: str
    title: str
    description: str
    impact_level: str
    recommended_action: str
    confidence: float
    generated_at: datetime


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    """
    Get comprehensive dashboard summary with AI insights.
    """
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        session = db_manager.get_session()
        
        try:
            # Get basic inventory stats
            total_items = session.query(InventoryItemDB).count()
            items = session.query(InventoryItemDB).all()
            
            total_value = sum(item.unit_cost * item.current_stock for item in items)
            low_stock_items = len([item for item in items if item.current_stock <= item.min_stock_threshold])
            out_of_stock_items = len([item for item in items if item.current_stock == 0])
            
            # Get sales data
            recent_sales = session.query(SalesDataDB).filter(
                SalesDataDB.date >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            # Calculate health score with AI
            health_data = {
                "total_items": total_items,
                "low_stock_ratio": low_stock_items / max(total_items, 1),
                "out_of_stock_ratio": out_of_stock_items / max(total_items, 1),
                "recent_sales_count": len(recent_sales),
                "avg_stock_level": sum(item.current_stock for item in items) / max(total_items, 1)
            }
            
            # Get AI insights
            ai_analysis = await ai_service.analyze_inventory_status(
                item_name="Overall Dashboard",
                current_stock=total_items,
                minimum_stock=0,
                context=health_data
            )
            
            health_score = int(ai_analysis.get("confidence", 0.8) * 100)
            
            return DashboardSummary(
                total_items=total_items,
                total_value=total_value,
                low_stock_items=low_stock_items,
                out_of_stock_items=out_of_stock_items,
                pending_orders=0,  # TODO: Implement orders tracking
                recent_alerts=low_stock_items + out_of_stock_items,
                health_score=health_score,
                last_updated=datetime.utcnow(),
                ai_insights=ai_analysis,
                recommendations=ai_analysis.get("next_actions", [])
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.get("/sales-analytics", response_model=SalesAnalytics)
async def get_sales_analytics(
    days: int = Query(30, description="Number of days to analyze")
):
    """
    Get sales analytics with AI predictions.
    """
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        session = db_manager.get_session()
        
        try:
            # Get sales data
            start_date = datetime.utcnow() - timedelta(days=days)
            sales = session.query(SalesDataDB).filter(
                SalesDataDB.date >= start_date
            ).all()
            
            total_sales = sum(sale.revenue for sale in sales)
            sales_count = len(sales)
            avg_order_value = total_sales / max(sales_count, 1)
            
            # Calculate top selling items
            item_sales = {}
            for sale in sales:
                if sale.sku not in item_sales:
                    item_sales[sale.sku] = {"quantity": 0, "revenue": 0}
                item_sales[sale.sku]["quantity"] += sale.quantity_sold
                item_sales[sale.sku]["revenue"] += sale.revenue
            
            top_selling = sorted(
                [{"sku": k, **v} for k, v in item_sales.items()],
                key=lambda x: x["revenue"],
                reverse=True
            )[:10]
            
            # Get AI forecast
            sales_data = {
                "total_sales": total_sales,
                "sales_count": sales_count,
                "avg_order_value": avg_order_value,
                "analysis_period_days": days,
                "top_items": top_selling[:5]
            }
            
            ai_forecast = await ai_service.analyze_inventory_status(
                item_name="Sales Analytics",
                current_stock=sales_count,
                minimum_stock=0,
                context=sales_data
            )
            
            return SalesAnalytics(
                total_sales=total_sales,
                sales_count=sales_count,
                avg_order_value=avg_order_value,
                top_selling_items=top_selling,
                sales_trend=ai_forecast.get("trend", "stable"),
                period_comparison={"previous_period": 0},  # TODO: Implement comparison
                ai_forecast=ai_forecast
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Sales analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sales analytics: {str(e)}")


@router.get("/inventory-overview", response_model=InventoryOverview)
async def get_inventory_overview():
    """
    Get inventory overview with AI optimization suggestions.
    """
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        session = db_manager.get_session()
        
        try:
            items = session.query(InventoryItemDB).all()
            
            # Calculate stats
            total_items = len(items)
            categories = list(set(item.category for item in items))
            
            # Stock distribution by category
            stock_distribution = {}
            for item in items:
                if item.category not in stock_distribution:
                    stock_distribution[item.category] = 0
                stock_distribution[item.category] += item.current_stock
            
            # Critical items (low stock or out of stock)
            critical_items = [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "current_stock": item.current_stock,
                    "min_threshold": item.min_stock_threshold,
                    "category": item.category,
                    "criticality": "out_of_stock" if item.current_stock == 0 else "low_stock"
                }
                for item in items
                if item.current_stock <= item.min_stock_threshold
            ]
            
            # Get AI optimization
            inventory_data = {
                "total_items": total_items,
                "categories": categories,
                "critical_items_count": len(critical_items),
                "stock_distribution": stock_distribution
            }
            
            ai_optimization = await ai_service.analyze_inventory_status(
                item_name="Inventory Overview",
                current_stock=total_items,
                minimum_stock=0,
                context=inventory_data
            )
            
            return InventoryOverview(
                total_items=total_items,
                categories=categories,
                stock_distribution=stock_distribution,
                critical_items=critical_items,
                optimization_suggestions=ai_optimization.get("next_actions", []),
                ai_health_score=ai_optimization.get("confidence", 0.8)
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Inventory overview error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get inventory overview: {str(e)}")


@router.get("/negotiations-summary", response_model=NegotiationSummary)
async def get_negotiations_summary():
    """
    Get negotiation summary with AI insights.
    """
    try:
        ai_service = await get_ai_service()
        
        # Get negotiation data from negotiation manager
        active_sessions = negotiation_manager.get_active_sessions()
        all_sessions = negotiation_manager.get_all_sessions()
        
        active_count = len(active_sessions)
        completed_count = len([s for s in all_sessions if not s.is_active])
        
        # Calculate success rate and savings
        successful_negotiations = len([
            s for s in all_sessions 
            if not s.is_active and s.current_offer <= s.target_price
        ])
        success_rate = successful_negotiations / max(completed_count, 1) * 100
        
        # Calculate average savings
        total_savings = sum([
            (s.initial_price - s.current_offer) 
            for s in all_sessions 
            if not s.is_active and s.current_offer < s.initial_price
        ])
        avg_savings = total_savings / max(completed_count, 1)
        
        # Get top suppliers
        supplier_stats = {}
        for session in all_sessions:
            supplier = session.supplier_name
            if supplier not in supplier_stats:
                supplier_stats[supplier] = {
                    "name": supplier,
                    "negotiations": 0,
                    "success_count": 0,
                    "total_savings": 0
                }
            
            supplier_stats[supplier]["negotiations"] += 1
            if not session.is_active and session.current_offer <= session.target_price:
                supplier_stats[supplier]["success_count"] += 1
                supplier_stats[supplier]["total_savings"] += (session.initial_price - session.current_offer)
        
        top_suppliers = sorted(
            supplier_stats.values(),
            key=lambda x: x["success_count"],
            reverse=True
        )[:5]
        
        # Get AI insights
        negotiation_data = {
            "active_negotiations": active_count,
            "completed_negotiations": completed_count,
            "success_rate": success_rate,
            "average_savings": avg_savings
        }
        
        ai_insights = await ai_service.analyze_inventory_status(
            item_name="Negotiation Analytics",
            current_stock=active_count,
            minimum_stock=0,
            context=negotiation_data
        )
        
        return NegotiationSummary(
            active_negotiations=active_count,
            completed_negotiations=completed_count,
            success_rate=success_rate,
            average_savings=avg_savings,
            top_suppliers=top_suppliers,
            ai_negotiation_insights=ai_insights
        )
        
    except Exception as e:
        logger.error(f"Negotiation summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get negotiation summary: {str(e)}")


@router.get("/insights", response_model=List[DashboardInsights])
async def get_dashboard_insights(
    limit: int = Query(10, description="Maximum number of insights to return")
):
    """
    Get AI-powered dashboard insights.
    """
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        session = db_manager.get_session()
        
        try:
            # Get data for AI analysis
            items = session.query(InventoryItemDB).all()
            recent_sales = session.query(SalesDataDB).filter(
                SalesDataDB.date >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            insights = []
            
            # Generate insights for different categories
            insight_categories = [
                "inventory_optimization",
                "sales_trends",
                "stock_alerts",
                "cost_analysis"
            ]
            
            for category in insight_categories:
                context_data = {
                    "category": category,
                    "total_items": len(items),
                    "recent_sales": len(recent_sales),
                    "low_stock_items": len([i for i in items if i.current_stock <= i.min_stock_threshold])
                }
                
                ai_analysis = await ai_service.analyze_inventory_status(
                    item_name=f"Dashboard Insight - {category}",
                    current_stock=len(items),
                    minimum_stock=0,
                    context=context_data
                )
                
                insight = DashboardInsights(
                    insight_type=category,
                    title=f"AI Insight: {category.replace('_', ' ').title()}",
                    description=ai_analysis.get("reasoning", "AI analysis completed"),
                    impact_level=ai_analysis.get("priority", "medium"),
                    recommended_action=ai_analysis.get("recommended_action", "Review data"),
                    confidence=ai_analysis.get("confidence", 0.8),
                    generated_at=datetime.utcnow()
                )
                
                insights.append(insight)
                
                if len(insights) >= limit:
                    break
            
            return insights
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Dashboard insights error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard insights: {str(e)}")


@router.post("/refresh-analytics")
async def refresh_analytics(background_tasks: BackgroundTasks):
    """
    Trigger background refresh of all analytics with AI analysis.
    """
    try:
        background_tasks.add_task(perform_analytics_refresh)
        
        return {
            "message": "Analytics refresh started",
            "status": "processing",
            "started_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Analytics refresh error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analytics refresh: {str(e)}")


async def perform_analytics_refresh():
    """
    Background task to refresh all analytics data.
    """
    try:
        logger.info("Starting analytics refresh...")
        
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # Refresh inventory analytics
        await refresh_inventory_analytics(ai_service, db_manager)
        
        # Refresh sales analytics
        await refresh_sales_analytics(ai_service, db_manager)
        
        # Refresh negotiation analytics
        await refresh_negotiation_analytics(ai_service)
        
        logger.info("Analytics refresh completed successfully")
        
    except Exception as e:
        logger.error(f"Analytics refresh failed: {e}")


async def refresh_inventory_analytics(ai_service, db_manager: DatabaseManager):
    """Refresh inventory analytics with AI analysis."""
    session = db_manager.get_session()
    
    try:
        items = session.query(InventoryItemDB).all()
        
        for item in items:
            # Analyze each item with AI
            analysis = await ai_service.analyze_inventory_status(
                item_name=item.name,
                current_stock=item.current_stock,
                minimum_stock=item.min_stock_threshold,
                item_sku=item.sku
            )
            
            # Store analysis results (in a real implementation, save to cache/database)
            logger.info(f"Analyzed {item.name}: {analysis.get('recommended_action')}")
            
    finally:
        session.close()


async def refresh_sales_analytics(ai_service, db_manager: DatabaseManager):
    """Refresh sales analytics with AI predictions."""
    session = db_manager.get_session()
    
    try:
        recent_sales = session.query(SalesDataDB).filter(
            SalesDataDB.date >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        sales_data = {
            "total_sales": len(recent_sales),
            "revenue": sum(sale.revenue for sale in recent_sales)
        }
        
        # Get AI predictions
        prediction = await ai_service.analyze_inventory_status(
            item_name="Sales Forecast",
            current_stock=len(recent_sales),
            minimum_stock=0,
            context=sales_data
        )
        
        logger.info(f"Sales forecast: {prediction.get('recommended_action')}")
        
    finally:
        session.close()


async def refresh_negotiation_analytics(ai_service):
    """Refresh negotiation analytics with AI insights."""
    try:
        active_sessions = negotiation_manager.get_active_sessions()
        
        negotiation_data = {
            "active_count": len(active_sessions),
            "total_sessions": len(negotiation_manager.get_all_sessions())
        }
        
        # Get AI insights
        insights = await ai_service.analyze_inventory_status(
            item_name="Negotiation Performance",
            current_stock=len(active_sessions),
            minimum_stock=0,
            context=negotiation_data
        )
        
        logger.info(f"Negotiation insights: {insights.get('recommended_action')}")
        
    except Exception as e:
        logger.error(f"Negotiation analytics refresh failed: {e}")


@router.get("/category-stats/{category}", response_model=CategoryStats)
async def get_category_stats(category: str):
    """
    Get detailed statistics for a specific category with AI analysis.
    """
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        session = db_manager.get_session()
        
        try:
            # Get items in category
            items = session.query(InventoryItemDB).filter(
                InventoryItemDB.category == category
            ).all()
            
            if not items:
                raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
            
            items_count = len(items)
            total_value = sum(item.unit_cost * item.current_stock for item in items)
            low_stock_count = len([item for item in items if item.current_stock <= item.min_stock_threshold])
            avg_stock_level = sum(item.current_stock for item in items) / items_count
            
            # Top items by value
            top_items = sorted(
                [
                    {
                        "sku": item.sku,
                        "name": item.name,
                        "current_stock": item.current_stock,
                        "value": item.unit_cost * item.current_stock
                    }
                    for item in items
                ],
                key=lambda x: x["value"],
                reverse=True
            )[:5]
            
            # Get AI analysis for category
            category_data = {
                "category": category,
                "items_count": items_count,
                "total_value": total_value,
                "low_stock_count": low_stock_count,
                "avg_stock_level": avg_stock_level
            }
            
            ai_analysis = await ai_service.analyze_inventory_status(
                item_name=f"Category Analysis - {category}",
                current_stock=items_count,
                minimum_stock=0,
                context=category_data
            )
            
            return CategoryStats(
                category=category,
                items_count=items_count,
                total_value=total_value,
                low_stock_count=low_stock_count,
                avg_stock_level=avg_stock_level,
                top_items=top_items,
                ai_analysis=ai_analysis,
                trend_prediction=ai_analysis.get("trend", "stable")
            )
            
        finally:
            session.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Category stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get category stats: {str(e)}")
        
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