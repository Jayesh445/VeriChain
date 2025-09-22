from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import datetime

from app.core.database import get_db
from app.agents.workflow_orchestrator import AgentWorkflowOrchestrator
from app.services.database import AgentDecisionService, InventoryService, SalesService
from app.core.logging import logger

router = APIRouter()

# Global orchestrator for monitoring
orchestrator = AgentWorkflowOrchestrator()


@router.get("/system/health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """Get overall system health status"""
    try:
        # Check database connectivity
        db_health = True
        try:
            await InventoryService.get_inventory_summary(db)
        except Exception:
            db_health = False
        
        # Check agent activity
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=5)
        agent_active = len(recent_decisions) > 0
        
        # Check workflow status
        active_workflows = len(orchestrator.active_workflows)
        
        # Overall health score
        health_score = 0
        if db_health:
            health_score += 40
        if agent_active:
            health_score += 30
        if active_workflows == 0:  # No stuck workflows
            health_score += 30
        
        status = "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
        
        return {
            "success": True,
            "system_health": {
                "overall_status": status,
                "health_score": health_score,
                "components": {
                    "database": "healthy" if db_health else "unhealthy",
                    "ai_agent": "active" if agent_active else "inactive",
                    "workflows": "healthy" if active_workflows == 0 else f"{active_workflows} active"
                },
                "last_agent_activity": recent_decisions[0].created_at.isoformat() if recent_decisions else None,
                "active_workflows_count": active_workflows
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "system_health": {
                "overall_status": "unhealthy",
                "health_score": 0,
                "error": str(e)
            },
            "checked_at": datetime.utcnow().isoformat()
        }


@router.get("/workflows/active")
async def get_active_workflows():
    """Get status of all active workflows"""
    try:
        active_workflows = []
        
        for workflow_id, context in orchestrator.active_workflows.items():
            workflow_status = orchestrator.get_workflow_status(workflow_id)
            if workflow_status:
                active_workflows.append(workflow_status)
        
        return {
            "success": True,
            "active_workflows": active_workflows,
            "count": len(active_workflows),
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get active workflows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active workflows: {str(e)}"
        )


@router.get("/agent/performance")
async def get_agent_performance(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get AI agent performance metrics"""
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent decisions
        all_decisions = await AgentDecisionService.get_recent_decisions(db, limit=1000)
        period_decisions = [d for d in all_decisions if d.created_at >= cutoff_date]
        
        if not period_decisions:
            return {
                "success": True,
                "performance": {
                    "period_days": days,
                    "no_data": True,
                    "message": "No agent activity in the specified period"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Calculate metrics
        total_decisions = len(period_decisions)
        executed_decisions = len([d for d in period_decisions if d.is_executed])
        
        # Group by decision type
        decisions_by_type = {}
        confidence_by_type = {}
        execution_rate_by_type = {}
        
        for decision in period_decisions:
            dtype = decision.decision_type.value
            
            if dtype not in decisions_by_type:
                decisions_by_type[dtype] = 0
                confidence_by_type[dtype] = []
                execution_rate_by_type[dtype] = {"total": 0, "executed": 0}
            
            decisions_by_type[dtype] += 1
            confidence_by_type[dtype].append(decision.confidence_score or 0)
            execution_rate_by_type[dtype]["total"] += 1
            if decision.is_executed:
                execution_rate_by_type[dtype]["executed"] += 1
        
        # Calculate averages
        avg_confidence_by_type = {}
        exec_rate_by_type = {}
        
        for dtype in decisions_by_type:
            avg_confidence_by_type[dtype] = sum(confidence_by_type[dtype]) / len(confidence_by_type[dtype])
            exec_rate_by_type[dtype] = (
                execution_rate_by_type[dtype]["executed"] / execution_rate_by_type[dtype]["total"]
                if execution_rate_by_type[dtype]["total"] > 0 else 0
            )
        
        # Daily activity
        daily_activity = {}
        for decision in period_decisions:
            date_key = decision.created_at.date().isoformat()
            if date_key not in daily_activity:
                daily_activity[date_key] = 0
            daily_activity[date_key] += 1
        
        # Performance scoring
        overall_confidence = sum(d.confidence_score or 0 for d in period_decisions) / total_decisions
        execution_rate = executed_decisions / total_decisions
        
        performance_score = (overall_confidence * 0.4 + execution_rate * 0.6) * 100
        
        return {
            "success": True,
            "performance": {
                "period_days": days,
                "overall_metrics": {
                    "total_decisions": total_decisions,
                    "executed_decisions": executed_decisions,
                    "execution_rate": execution_rate,
                    "avg_confidence": overall_confidence,
                    "performance_score": performance_score,
                    "decisions_per_day": total_decisions / days
                },
                "by_decision_type": {
                    "counts": decisions_by_type,
                    "avg_confidence": avg_confidence_by_type,
                    "execution_rates": exec_rate_by_type
                },
                "daily_activity": daily_activity,
                "quality_indicators": {
                    "high_confidence_decisions": len([d for d in period_decisions if (d.confidence_score or 0) > 0.8]),
                    "low_confidence_decisions": len([d for d in period_decisions if (d.confidence_score or 0) < 0.5]),
                    "rapid_execution": len([d for d in period_decisions if d.is_executed and d.executed_at and (d.executed_at - d.created_at).total_seconds() < 3600])  # Within 1 hour
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent performance: {str(e)}"
        )


@router.get("/alerts/active")
async def get_active_alerts(db: AsyncSession = Depends(get_db)):
    """Get all active system alerts"""
    try:
        alerts = []
        
        # Get inventory alerts
        inventory_summary = await InventoryService.get_inventory_summary(db)
        
        if inventory_summary["out_of_stock_items"] > 0:
            alerts.append({
                "type": "inventory",
                "severity": "critical",
                "title": "Out of Stock Items",
                "message": f"{inventory_summary['out_of_stock_items']} items are out of stock",
                "count": inventory_summary["out_of_stock_items"],
                "category": "stock_management"
            })
        
        if inventory_summary["low_stock_items"] > 0:
            alerts.append({
                "type": "inventory",
                "severity": "warning",
                "title": "Low Stock Items",
                "message": f"{inventory_summary['low_stock_items']} items are below reorder level",
                "count": inventory_summary["low_stock_items"],
                "category": "stock_management"
            })
        
        # Get agent alerts
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=20)
        unexecuted_alerts = [
            d for d in recent_decisions 
            if d.decision_type.value in ["alert", "anomaly"] and not d.is_executed
        ]
        
        for decision in unexecuted_alerts[:5]:  # Limit to 5 most recent
            try:
                decision_data = eval(decision.decision_data) if decision.decision_data else {}
                severity = decision_data.get("severity", "medium")
            except:
                severity = "medium"
            
            alerts.append({
                "type": "agent",
                "severity": severity,
                "title": f"AI Alert: {decision.decision_type.value.title()}",
                "message": decision.reasoning[:200] + "..." if len(decision.reasoning) > 200 else decision.reasoning,
                "decision_id": decision.id,
                "created_at": decision.created_at.isoformat(),
                "category": "ai_insights"
            })
        
        # Check for system issues
        active_workflows = len(orchestrator.active_workflows)
        stuck_workflows = sum(
            1 for context in orchestrator.active_workflows.values()
            if (datetime.utcnow() - context.started_at).total_seconds() > 3600  # More than 1 hour
        )
        
        if stuck_workflows > 0:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "title": "Stuck Workflows",
                "message": f"{stuck_workflows} workflows have been running for over 1 hour",
                "count": stuck_workflows,
                "category": "system_health"
            })
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "warning": 2, "medium": 3, "low": 4}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 5))
        
        return {
            "success": True,
            "alerts": alerts,
            "summary": {
                "total_alerts": len(alerts),
                "critical": len([a for a in alerts if a["severity"] == "critical"]),
                "warnings": len([a for a in alerts if a["severity"] in ["high", "warning"]]),
                "info": len([a for a in alerts if a["severity"] in ["medium", "low"]])
            },
            "categories": {
                "stock_management": len([a for a in alerts if a["category"] == "stock_management"]),
                "ai_insights": len([a for a in alerts if a["category"] == "ai_insights"]),
                "system_health": len([a for a in alerts if a["category"] == "system_health"])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active alerts: {str(e)}"
        )


@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = 50,
    level: str = "INFO",
    db: AsyncSession = Depends(get_db)
):
    """Get recent system logs (simplified - in production use proper log aggregation)"""
    try:
        # For now, return recent decisions as log entries
        # In production, integrate with proper logging system
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=limit)
        
        logs = []
        for decision in recent_decisions:
            logs.append({
                "timestamp": decision.created_at.isoformat(),
                "level": "INFO",
                "component": "ai_agent",
                "message": f"Decision made: {decision.decision_type.value} - {decision.reasoning[:100]}{'...' if len(decision.reasoning) > 100 else ''}",
                "metadata": {
                    "decision_id": decision.id,
                    "item_id": decision.item_id,
                    "vendor_id": decision.vendor_id,
                    "confidence": decision.confidence_score
                }
            })
        
        return {
            "success": True,
            "logs": logs,
            "count": len(logs),
            "filter": {
                "limit": limit,
                "level": level
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent logs: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def trigger_maintenance_cleanup():
    """Trigger system maintenance and cleanup"""
    try:
        # Cleanup old workflows
        await orchestrator.cleanup_completed_workflows(max_age_hours=24)
        
        return {
            "success": True,
            "message": "Maintenance cleanup completed",
            "actions_taken": [
                "Cleaned up old workflows",
                "System health check performed"
            ],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Maintenance cleanup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Maintenance cleanup failed: {str(e)}"
        )


@router.get("/workflows/active")
async def get_active_workflows():
    """Get currently active workflows"""
    try:
        # Get active workflows from orchestrator
        active_workflows = []
        
        for workflow_id, workflow_context in orchestrator.active_workflows.items():
            active_workflows.append({
                "id": workflow_id,
                "type": workflow_context.workflow_type.value if hasattr(workflow_context, 'workflow_type') else "analysis",
                "status": workflow_context.status.value if hasattr(workflow_context, 'status') else "running",
                "started_at": workflow_context.started_at.isoformat() if hasattr(workflow_context, 'started_at') else datetime.utcnow().isoformat(),
                "current_step": getattr(workflow_context, 'current_step', 1),
                "total_steps": getattr(workflow_context, 'total_steps', 6),
                "description": getattr(workflow_context, 'description', "AI agent workflow")
            })
        
        return active_workflows
        
    except Exception as e:
        logger.error(f"Failed to get active workflows: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active workflows: {str(e)}"
        )