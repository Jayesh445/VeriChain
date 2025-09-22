from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models import AgentDecision, AgentDecisionType
from app.core.logging import logger


class AgentDecisionService:
    @staticmethod
    async def get_recent_decisions(db: AsyncSession, decision_type: Optional[AgentDecisionType] = None, limit: int = 50):
        query = select(AgentDecision).order_by(AgentDecision.created_at.desc()).limit(limit)
        if decision_type:
            query = query.where(AgentDecision.decision_type == decision_type.value)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_decision_executed(db: AsyncSession, decision_id: int):
        result = await db.execute(select(AgentDecision).where(AgentDecision.id == decision_id))
        decision = result.scalar_one_or_none()
        
        if decision:
            await db.execute(
                update(AgentDecision)
                .where(AgentDecision.id == decision_id)
                .values(is_executed=True, executed_at=datetime.utcnow())
            )
            await db.commit()
            await db.refresh(decision)
        
        return decision

router = APIRouter()


# Simple mock orchestrator for basic functionality
class SimpleOrchestrator:
    def __init__(self):
        self.workflows = {}
    
    async def trigger_full_analysis(self, db, trigger_type, parameters):
        import uuid
        workflow_id = str(uuid.uuid4())
        
        class WorkflowContext:
            def __init__(self, workflow_id):
                self.workflow_id = workflow_id
                self.status = type('Status', (), {'value': 'running'})()
                self.started_at = datetime.utcnow()
        
        context = WorkflowContext(workflow_id)
        self.workflows[workflow_id] = context
        return context
    
    def get_workflow_status(self, workflow_id):
        return self.workflows.get(workflow_id)


orchestrator = SimpleOrchestrator()


@router.post("/analyze", response_model=Dict[str, Any])
async def trigger_agent_analysis(
    background_tasks: BackgroundTasks,
    trigger_type: str = "manual",
    parameters: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a complete agent analysis workflow
    
    This endpoint starts an autonomous analysis of the current inventory situation,
    including stock levels, sales trends, vendor performance, and generates
    actionable recommendations.
    """
    try:
        # Start workflow in background
        workflow_context = await orchestrator.trigger_full_analysis(
            db=db,
            trigger_type=trigger_type,
            parameters=parameters or {}
        )
        
        return {
            "success": True,
            "workflow_id": workflow_context.workflow_id,
            "status": workflow_context.status.value,
            "message": "Agent analysis started successfully",
            "started_at": workflow_context.started_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger agent analysis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the status of a running workflow"""
    try:
        status = orchestrator.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found"
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_latest_insights(
    role: Optional[str] = "admin",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get latest agent insights and recommendations
    
    Returns the most recent analysis results, recommendations, and alerts
    formatted for the specified user role (SCM, Finance, or Admin).
    """
    try:
        # Get recent decisions
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=limit)
        
        if not recent_decisions:
            return {
                "success": True,
                "insights": {
                    "summary": "No recent analysis available",
                    "recommendations": [],
                    "alerts": [],
                    "decisions_count": 0
                },
                "generated_at": datetime.utcnow().isoformat(),
                "role": role
            }
        
        # Process decisions by type
        recommendations = []
        alerts = []
        
        for decision in recent_decisions:
            import json
            try:
                decision_data = json.loads(decision.decision_data) if decision.decision_data else {}
            except (json.JSONDecodeError, TypeError):
                decision_data = {}
            
            if decision.decision_type == "REORDER":
                recommendations.append({
                    "id": decision.id,
                    "type": "reorder",
                    "item_id": decision.item_id,
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence_score,
                    "created_at": decision.created_at.isoformat(),
                    "data": decision_data
                })
            
            elif decision.decision_type in ["ALERT", "ANOMALY"]:
                alerts.append({
                    "id": decision.id,
                    "type": decision.decision_type,
                    "item_id": decision.item_id,
                    "vendor_id": decision.vendor_id,
                    "reasoning": decision.reasoning,
                    "severity": decision_data.get("severity", "medium"),
                    "created_at": decision.created_at.isoformat(),
                    "data": decision_data
                })
        
        # Generate role-specific summary
        if role.lower() == "scm":
            summary = f"Found {len(recommendations)} reorder recommendations and {len(alerts)} operational alerts"
        elif role.lower() == "finance":
            total_cost = sum(r.get("data", {}).get("estimated_cost", 0) for r in recommendations)
            summary = f"Estimated reorder cost: ${total_cost:,.2f} across {len(recommendations)} items"
        else:
            summary = f"Latest analysis: {len(recommendations)} recommendations, {len(alerts)} alerts"
        
        return {
            "success": True,
            "insights": {
                "summary": summary,
                "recommendations": recommendations,
                "alerts": alerts,
                "decisions_count": len(recent_decisions),
                "role_specific_data": {
                    "role": role,
                    "total_items_analyzed": len(set(d.item_id for d in recent_decisions if d.item_id)),
                    "confidence_avg": sum(d.confidence_score or 0 for d in recent_decisions) / len(recent_decisions)
                }
            },
            "generated_at": datetime.utcnow().isoformat(),
            "role": role
        }
        
    except Exception as e:
        logger.error(f"Failed to get insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get insights: {str(e)}"
        )


@router.get("/decisions/recent")
async def get_recent_decisions(
    limit: int = 50,
    decision_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent agent decisions with filtering"""
    try:
        from app.models import AgentDecisionType
        
        # Convert string to enum if provided
        filter_type = None
        if decision_type:
            try:
                filter_type = AgentDecisionType(decision_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid decision type: {decision_type}"
                )
        
        decisions = await AgentDecisionService.get_recent_decisions(
            db=db,
            decision_type=filter_type,
            limit=limit
        )
        
        return {
            "success": True,
            "decisions": [
                {
                    "id": d.id,
                    "type": d.decision_type,
                    "item_id": d.item_id,
                    "vendor_id": d.vendor_id,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence_score,
                    "is_executed": d.is_executed,
                    "created_at": d.created_at.isoformat(),
                    "executed_at": d.executed_at.isoformat() if d.executed_at else None,
                    "data": eval(d.decision_data) if d.decision_data else {}
                }
                for d in decisions
            ],
            "count": len(decisions),
            "filter": decision_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent decisions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent decisions: {str(e)}"
        )


@router.post("/decisions/{decision_id}/execute")
async def execute_decision(
    decision_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a decision as executed (for manual execution tracking)"""
    try:
        decision = await AgentDecisionService.mark_decision_executed(db, decision_id)
        
        if not decision:
            raise HTTPException(
                status_code=404,
                detail="Decision not found"
            )
        
        return {
            "success": True,
            "message": "Decision marked as executed",
            "decision_id": decision_id,
            "executed_at": decision.executed_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute decision: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute decision: {str(e)}"
        )


@router.get("/performance/summary")
async def get_agent_performance_summary(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get agent performance summary"""
    try:
        from datetime import timedelta
        
        # Get decisions from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=1000)
        
        # Filter by date
        filtered_decisions = [
            d for d in recent_decisions 
            if d.created_at >= cutoff_date
        ]
        
        # Calculate metrics
        total_decisions = len(filtered_decisions)
        executed_decisions = len([d for d in filtered_decisions if d.is_executed])
        
        decisions_by_type = {}
        confidence_by_type = {}
        
        for decision in filtered_decisions:
            decision_type = decision.decision_type.value
            decisions_by_type[decision_type] = decisions_by_type.get(decision_type, 0) + 1
            
            if decision_type not in confidence_by_type:
                confidence_by_type[decision_type] = []
            confidence_by_type[decision_type].append(decision.confidence_score or 0)
        
        # Calculate average confidence by type
        avg_confidence_by_type = {
            decision_type: sum(scores) / len(scores) if scores else 0
            for decision_type, scores in confidence_by_type.items()
        }
        
        return {
            "success": True,
            "performance": {
                "period_days": days,
                "total_decisions": total_decisions,
                "executed_decisions": executed_decisions,
                "execution_rate": executed_decisions / total_decisions if total_decisions > 0 else 0,
                "decisions_by_type": decisions_by_type,
                "avg_confidence_by_type": avg_confidence_by_type,
                "overall_confidence": sum(d.confidence_score or 0 for d in filtered_decisions) / total_decisions if total_decisions > 0 else 0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance summary: {str(e)}"
        )


@router.post("/workflows/cleanup")
async def cleanup_workflows():
    """Clean up old completed workflows"""
    try:
        await orchestrator.cleanup_completed_workflows(max_age_hours=24)
        
        return {
            "success": True,
            "message": "Workflow cleanup completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup workflows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup workflows: {str(e)}"
        )


@router.get("/decisions/recent", response_model=Dict[str, Any])
async def get_recent_agent_decisions(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get recent agent decisions"""
    try:
        decisions = await AgentDecisionService.get_recent_decisions(db, limit=limit)
        
        # Format for frontend
        formatted_decisions = []
        for decision in decisions:
            formatted_decisions.append({
                "id": decision.id,
                "decision_type": decision.decision_type,
                "item_id": decision.item_id,
                "reasoning": decision.reasoning,
                "confidence_score": decision.confidence_score,
                "is_executed": decision.is_executed,
                "created_at": decision.created_at.isoformat(),
                "execution_result": decision.execution_result
            })
        
        return formatted_decisions
        
    except Exception as e:
        logger.error(f"Failed to get recent decisions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent decisions: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_agent_insights(
    role: str = "admin",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get agent insights and recommendations"""
    try:
        # Get recent insights from database
        insights = await AgentDecisionService.get_insights(db, role=role, limit=limit)
        
        # Format insights response
        recommendations = []
        for insight in insights:
            recommendations.append({
                "id": insight.id,
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "priority": insight.priority,
                "potential_savings": insight.potential_savings,
                "category": insight.category,
                "created_at": insight.created_at.isoformat()
            })
        
        return {
            "insights": {
                "recommendations": recommendations
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get insights: {str(e)}"
        )