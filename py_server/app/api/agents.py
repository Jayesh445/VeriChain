"""
FastAPI router for agent operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

try:
    from fastapi import APIRouter, HTTPException, BackgroundTasks
    from pydantic import BaseModel
except ImportError:
    # Fallback for when FastAPI is not available during static analysis
    class APIRouter:
        def __init__(self, **kwargs): pass
        def post(self, *args, **kwargs): return lambda f: f
        def get(self, *args, **kwargs): return lambda f: f
    
    class HTTPException(Exception): pass
    class BackgroundTasks: pass
    class BaseModel: pass

from app.models import (
    AgentRequest, AgentResponse, AgentDecision, AgentOverride,
    InventoryItem, SalesData, SupplierInfo, Priority, ActionType
)
from app.agents.stationery_agent import create_stationery_agent
from app.services.notifications import notification_manager, send_order_alert
from app.services.database import db_manager

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentAnalysisRequest(BaseModel):
    """Request model for agent analysis."""
    inventory_items: List[InventoryItem]
    sales_data: Optional[List[SalesData]] = None
    supplier_data: Optional[List[SupplierInfo]] = None
    user_query: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentAnalysisResponse(BaseModel):
    """Response model for agent analysis."""
    success: bool
    decisions: List[AgentDecision]
    summary: str
    dashboard_insights: Dict[str, Any]
    processing_time: float
    total_recommendations: int
    critical_alerts: int
    estimated_total_cost: float


@router.post("/analyze", response_model=AgentAnalysisResponse)
async def analyze_inventory(
    request: AgentAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze stationery inventory and generate recommendations.
    """
    start_time = datetime.utcnow()
    
    try:
        # If no inventory data provided, get from database
        if not request.inventory_items:
            request.inventory_items = await db_manager.get_inventory_items(limit=500)
        
        # If no sales data provided, get from database
        if not request.sales_data:
            request.sales_data = await db_manager.get_sales_data(days=365)
        
        # Create stationery agent
        agent = create_stationery_agent()
        
        # Analyze inventory portfolio
        decisions = agent.analyze_stationery_portfolio(
            inventory_items=request.inventory_items,
            sales_data=request.sales_data or [],
            supplier_data=request.supplier_data or []
        )
        
        # Save decisions to database
        for decision in decisions:
            await db_manager.save_agent_decision(decision)
        
        # Get dashboard insights
        dashboard_insights = agent.get_dashboard_insights(
            inventory_items=request.inventory_items,
            sales_data=request.sales_data or []
        )
        
        # Calculate statistics
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        critical_alerts = len([d for d in decisions if d.priority in [Priority.CRITICAL, Priority.HIGH]])
        estimated_total_cost = sum(d.estimated_cost or 0 for d in decisions)
        
        # Generate summary
        summary_parts = [
            f"Analyzed {len(request.inventory_items)} stationery items",
            f"Generated {len(decisions)} recommendations",
            f"Found {critical_alerts} critical/high priority actions"
        ]
        
        if estimated_total_cost > 0:
            summary_parts.append(f"Total estimated order value: ${estimated_total_cost:,.2f}")
        
        summary = ". ".join(summary_parts) + "."
        
        # Send notifications for critical decisions (in background)
        background_tasks.add_task(
            notification_manager.process_decisions, 
            [d for d in decisions if d.priority in [Priority.CRITICAL, Priority.HIGH]]
        )
        
        return AgentAnalysisResponse(
            success=True,
            decisions=decisions,
            summary=summary,
            dashboard_insights=dashboard_insights,
            processing_time=processing_time,
            total_recommendations=len(decisions),
            critical_alerts=critical_alerts,
            estimated_total_cost=estimated_total_cost
        )
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed after {processing_time:.2f}s: {str(e)}"
        )


@router.get("/decisions", response_model=List[AgentDecision])
async def get_recent_decisions(
    limit: int = 50,
    priority: Optional[Priority] = None,
    action_type: Optional[ActionType] = None
):
    """
    Get recent agent decisions with optional filtering.
    """
    try:
        decisions = await db_manager.get_agent_decisions(limit=limit)
        
        # Apply filters
        if priority:
            decisions = [d for d in decisions if d.priority == priority]
        
        if action_type:
            decisions = [d for d in decisions if d.action_type == action_type]
        
        return decisions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get decisions: {str(e)}"
        )


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(
    decision_id: UUID,
    background_tasks: BackgroundTasks,
    override: Optional[AgentOverride] = None
):
    """
    Approve or modify an agent decision.
    """
    try:
        # Approve decision in database
        success = await db_manager.approve_decision(decision_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Decision {decision_id} not found"
            )
        
        # TODO: Trigger actual ordering process here
        # This would integrate with supplier APIs, purchasing systems, etc.
        
        return {
            "success": True,
            "message": f"Decision {decision_id} approved successfully",
            "override_applied": override is not None,
            "next_steps": [
                "Order will be processed",
                "Supplier will be contacted",
                "Delivery tracking will be updated"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve decision: {str(e)}"
        )


@router.get("/insights/seasonal")
async def get_seasonal_insights():
    """
    Get seasonal insights for stationery inventory.
    """
    current_month = datetime.now().month
    
    # Educational calendar insights
    seasonal_events = {
        3: "Exam preparation season - increase writing instruments stock",
        4: "School preparation begins - focus on textbooks and essentials",
        5: "Admission season - art supplies and stationery sets in demand",
        6: "School opening rush - all categories high demand",
        7: "Back-to-school continues - monitor fast-moving items",
        8: "Mid-session restocking needed",
        9: "Festival season - gift stationery items popular",
        10: "Mid-term preparation - study materials in demand",
        11: "Exam season approaching - writing materials critical",
        12: "Year-end exams - peak demand for exam essentials",
        1: "New year session - fresh supplies needed",
        2: "Winter session continuation - steady demand"
    }
    
    upcoming_events = []
    for month in range(current_month, min(current_month + 4, 13)):
        if month in seasonal_events:
            upcoming_events.append({
                "month": month,
                "event": seasonal_events[month],
                "days_ahead": (datetime(datetime.now().year, month, 1) - datetime.now()).days
            })
    
    return {
        "current_month_insight": seasonal_events.get(current_month, "Regular inventory management"),
        "upcoming_events": upcoming_events,
        "recommendations": [
            "Plan inventory 30 days before peak seasons",
            "Negotiate bulk discounts for seasonal orders",
            "Monitor fast-moving items during peak periods",
            "Maintain safety stock for critical items"
        ]
    }


@router.get("/insights/categories")
async def get_category_insights():
    """
    Get insights about different stationery categories.
    """
    from app.agents.stationery_agent import StationeryCategory, StationeryPatternDatabase
    
    category_insights = {}
    
    for category in StationeryCategory:
        pattern = StationeryPatternDatabase.get_pattern(category)
        current_month = datetime.now().month
        is_peak = StationeryPatternDatabase.is_peak_season(category, current_month)
        multiplier = StationeryPatternDatabase.get_demand_multiplier(category, current_month)
        
        category_insights[category.value] = {
            "description": pattern.description,
            "peak_months": pattern.peak_months,
            "current_status": "Peak Season" if is_peak else "Regular Season",
            "demand_multiplier": multiplier,
            "recommended_lead_time_adjustment": pattern.lead_time_adjustment,
            "next_peak": next((m for m in pattern.peak_months if m > current_month), pattern.peak_months[0])
        }
    
    return {
        "categories": category_insights,
        "current_month": current_month,
        "general_recommendations": [
            "Stock up 2-3 weeks before peak seasons",
            "Monitor exam calendars for demand spikes",
            "Leverage bulk ordering during off-peak periods",
            "Maintain category-specific safety stocks"
        ]
    }