"""
Stock Monitoring API with Real-time AI Insights
Provides endpoints for continuous stock monitoring with Gemini AI analysis.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from loguru import logger

from app.services.ai_service import get_ai_service
from app.services.database import DatabaseManager
from app.models.database import InventoryItemDB, SalesDataDB, AlertDB
from app.services.notifications_enhanced import notification_manager

router = APIRouter(prefix="/api/v1/monitoring", tags=["stock-monitoring"])

# Global monitoring state
monitoring_tasks: Dict[str, Dict[str, Any]] = {}
active_monitors: Dict[str, bool] = {}


class MonitoringConfig(BaseModel):
    """Configuration for stock monitoring."""
    interval_minutes: int = 5
    enable_alerts: bool = True
    alert_threshold_days: int = 7
    enable_predictions: bool = True
    categories: Optional[List[str]] = None
    priority_items: Optional[List[str]] = None


class MonitoringStatus(BaseModel):
    """Current monitoring status."""
    is_active: bool
    monitor_id: str
    started_at: datetime
    last_check: Optional[datetime]
    items_monitored: int
    alerts_generated: int
    insights_count: int
    config: MonitoringConfig


class StockInsight(BaseModel):
    """AI-generated stock insight."""
    insight_id: str
    insight_type: str
    item_sku: str
    item_name: str
    current_stock: int
    predicted_stockout_days: Optional[int]
    recommendation: str
    confidence: float
    priority: str
    generated_at: datetime
    ai_reasoning: str


class MonitoringReport(BaseModel):
    """Comprehensive monitoring report."""
    report_id: str
    generated_at: datetime
    summary: Dict[str, Any]
    insights: List[StockInsight]
    recommendations: List[str]
    performance_metrics: Dict[str, Any]


@router.post("/start", response_model=MonitoringStatus)
async def start_stock_monitoring(
    config: MonitoringConfig,
    background_tasks: BackgroundTasks
):
    """
    Start continuous stock monitoring with AI analysis.
    """
    try:
        monitor_id = f"monitor_{uuid4().hex[:8]}"
        
        # Initialize monitoring state
        monitoring_tasks[monitor_id] = {
            "config": config,
            "started_at": datetime.utcnow(),
            "last_check": None,
            "items_monitored": 0,
            "alerts_generated": 0,
            "insights_count": 0,
            "task": None
        }
        
        active_monitors[monitor_id] = True
        
        # Start background monitoring task
        background_tasks.add_task(
            continuous_stock_monitoring,
            monitor_id,
            config
        )
        
        logger.info(f"Started stock monitoring: {monitor_id}")
        
        return MonitoringStatus(
            is_active=True,
            monitor_id=monitor_id,
            started_at=monitoring_tasks[monitor_id]["started_at"],
            last_check=None,
            items_monitored=0,
            alerts_generated=0,
            insights_count=0,
            config=config
        )
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.get("/status/{monitor_id}", response_model=MonitoringStatus)
async def get_monitoring_status(monitor_id: str):
    """
    Get current status of a monitoring session.
    """
    if monitor_id not in monitoring_tasks:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    task_data = monitoring_tasks[monitor_id]
    
    return MonitoringStatus(
        is_active=active_monitors.get(monitor_id, False),
        monitor_id=monitor_id,
        started_at=task_data["started_at"],
        last_check=task_data["last_check"],
        items_monitored=task_data["items_monitored"],
        alerts_generated=task_data["alerts_generated"],
        insights_count=task_data["insights_count"],
        config=task_data["config"]
    )


@router.post("/stop/{monitor_id}")
async def stop_monitoring(monitor_id: str):
    """
    Stop a specific monitoring session.
    """
    if monitor_id not in monitoring_tasks:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    active_monitors[monitor_id] = False
    logger.info(f"Stopped monitoring: {monitor_id}")
    
    return {"message": f"Monitoring {monitor_id} stopped", "stopped_at": datetime.utcnow()}


@router.get("/insights/{monitor_id}", response_model=List[StockInsight])
async def get_monitoring_insights(
    monitor_id: str,
    limit: int = Query(50, description="Maximum number of insights to return")
):
    """
    Get AI-generated insights from monitoring session.
    """
    if monitor_id not in monitoring_tasks:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    try:
        # Get insights from monitoring cache or generate new ones
        insights = await generate_stock_insights(monitor_id, limit)
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.get("/report/{monitor_id}", response_model=MonitoringReport)
async def get_monitoring_report(monitor_id: str):
    """
    Get comprehensive monitoring report with AI analysis.
    """
    if monitor_id not in monitoring_tasks:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    try:
        ai_service = await get_ai_service()
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # Generate comprehensive report
        report = await generate_monitoring_report(monitor_id, ai_service, db_manager)
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/active-monitors")
async def get_active_monitors():
    """
    Get list of all active monitoring sessions.
    """
    active = [
        {
            "monitor_id": monitor_id,
            "is_active": is_active,
            "started_at": monitoring_tasks[monitor_id]["started_at"],
            "last_check": monitoring_tasks[monitor_id]["last_check"]
        }
        for monitor_id, is_active in active_monitors.items()
        if is_active and monitor_id in monitoring_tasks
    ]
    
    return {"active_monitors": active, "total_active": len(active)}


async def continuous_stock_monitoring(monitor_id: str, config: MonitoringConfig):
    """
    Background task for continuous stock monitoring.
    """
    ai_service = await get_ai_service()
    db_manager = DatabaseManager()
    
    try:
        await db_manager.connect()
        logger.info(f"Starting continuous monitoring: {monitor_id}")
        
        while active_monitors.get(monitor_id, False):
            try:
                # Perform monitoring cycle
                await perform_monitoring_cycle(monitor_id, config, ai_service, db_manager)
                
                # Update last check time
                monitoring_tasks[monitor_id]["last_check"] = datetime.utcnow()
                
                # Wait for next cycle
                await asyncio.sleep(config.interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Monitoring cycle error for {monitor_id}: {e}")
                await asyncio.sleep(30)  # Wait before retrying
                
    except Exception as e:
        logger.error(f"Monitoring task failed for {monitor_id}: {e}")
    finally:
        active_monitors[monitor_id] = False
        logger.info(f"Monitoring stopped: {monitor_id}")


async def perform_monitoring_cycle(monitor_id: str, config: MonitoringConfig, 
                                 ai_service, db_manager: DatabaseManager):
    """
    Perform a single monitoring cycle with AI analysis.
    """
    session = db_manager.get_session()
    
    try:
        # Get inventory items
        query = session.query(InventoryItemDB)
        if config.categories:
            query = query.filter(InventoryItemDB.category.in_(config.categories))
        
        items = query.all()
        monitoring_tasks[monitor_id]["items_monitored"] = len(items)
        
        # Analyze each item with AI
        insights = []
        alerts_generated = 0
        
        for item in items:
            try:
                # Get AI analysis for this item
                analysis = await ai_service.analyze_inventory_status(
                    item_name=item.name,
                    current_stock=item.current_stock,
                    minimum_stock=item.min_stock_threshold,
                    item_sku=item.sku
                )
                
                # Generate insight
                insight = StockInsight(
                    insight_id=f"insight_{uuid4().hex[:8]}",
                    insight_type=analysis.get("alert_type", "normal"),
                    item_sku=item.sku,
                    item_name=item.name,
                    current_stock=item.current_stock,
                    predicted_stockout_days=analysis.get("predicted_days"),
                    recommendation=analysis.get("recommended_action", "No action needed"),
                    confidence=analysis.get("confidence", 0.8),
                    priority=analysis.get("priority", "medium"),
                    generated_at=datetime.utcnow(),
                    ai_reasoning=analysis.get("reasoning", "AI analysis completed")
                )
                
                insights.append(insight)
                
                # Generate alerts if needed
                if analysis.get("alert_type") in ["urgent", "critical"]:
                    await generate_monitoring_alert(item, analysis, monitor_id)
                    alerts_generated += 1
                    
            except Exception as e:
                logger.error(f"Item analysis failed for {item.sku}: {e}")
        
        # Update monitoring metrics
        monitoring_tasks[monitor_id]["insights_count"] += len(insights)
        monitoring_tasks[monitor_id]["alerts_generated"] += alerts_generated
        
        # Cache insights for API access
        monitoring_tasks[monitor_id]["latest_insights"] = insights[:50]  # Keep last 50
        
        logger.info(f"Monitoring cycle completed for {monitor_id}: {len(insights)} insights, {alerts_generated} alerts")
        
    finally:
        session.close()


async def generate_stock_insights(monitor_id: str, limit: int) -> List[StockInsight]:
    """
    Generate or retrieve stock insights for a monitoring session.
    """
    if monitor_id in monitoring_tasks and "latest_insights" in monitoring_tasks[monitor_id]:
        return monitoring_tasks[monitor_id]["latest_insights"][:limit]
    
    # Generate new insights if none cached
    ai_service = await get_ai_service()
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    session = db_manager.get_session()
    try:
        items = session.query(InventoryItemDB).limit(limit).all()
        insights = []
        
        for item in items:
            analysis = await ai_service.analyze_inventory_status(
                item_name=item.name,
                current_stock=item.current_stock,
                minimum_stock=item.min_stock_threshold,
                item_sku=item.sku
            )
            
            insight = StockInsight(
                insight_id=f"insight_{uuid4().hex[:8]}",
                insight_type=analysis.get("alert_type", "normal"),
                item_sku=item.sku,
                item_name=item.name,
                current_stock=item.current_stock,
                predicted_stockout_days=analysis.get("predicted_days"),
                recommendation=analysis.get("recommended_action", "Monitor stock levels"),
                confidence=analysis.get("confidence", 0.8),
                priority=analysis.get("priority", "medium"),
                generated_at=datetime.utcnow(),
                ai_reasoning=analysis.get("reasoning", "AI analysis completed")
            )
            
            insights.append(insight)
            
        return insights
        
    finally:
        session.close()


async def generate_monitoring_report(monitor_id: str, ai_service, db_manager: DatabaseManager) -> MonitoringReport:
    """
    Generate comprehensive monitoring report with AI analysis.
    """
    task_data = monitoring_tasks[monitor_id]
    
    # Get recent insights
    insights = await generate_stock_insights(monitor_id, 100)
    
    # Generate AI summary
    summary_data = {
        "total_items": task_data["items_monitored"],
        "monitoring_duration": (datetime.utcnow() - task_data["started_at"]).total_seconds() / 3600,
        "alerts_generated": task_data["alerts_generated"],
        "insights_generated": task_data["insights_count"]
    }
    
    # Get AI recommendations
    recommendations = await ai_service.analyze_inventory_status(
        item_name="Overall Inventory",
        current_stock=summary_data["total_items"],
        minimum_stock=0,
        context=summary_data
    )
    
    return MonitoringReport(
        report_id=f"report_{uuid4().hex[:8]}",
        generated_at=datetime.utcnow(),
        summary=summary_data,
        insights=insights,
        recommendations=recommendations.get("next_actions", []),
        performance_metrics={
            "avg_confidence": sum(i.confidence for i in insights) / len(insights) if insights else 0,
            "critical_items": len([i for i in insights if i.priority == "critical"]),
            "high_priority_items": len([i for i in insights if i.priority == "high"]),
            "monitoring_efficiency": task_data["insights_count"] / max(task_data["items_monitored"], 1)
        }
    )


async def generate_monitoring_alert(item: InventoryItemDB, analysis: Dict[str, Any], monitor_id: str):
    """
    Generate alert for critical stock situations.
    """
    try:
        await notification_manager.send_inventory_alert(
            item_name=item.name,
            current_stock=item.current_stock,
            minimum_stock=item.min_stock_threshold,
            alert_type=analysis.get("alert_type", "warning"),
            additional_context={
                "monitor_id": monitor_id,
                "ai_reasoning": analysis.get("reasoning"),
                "recommended_action": analysis.get("recommended_action")
            }
        )
    except Exception as e:
        logger.error(f"Failed to send monitoring alert: {e}")