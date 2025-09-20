"""
Advanced Agent Orchestration API Endpoints
Implements the complete PlantUML workflow with multiple specialized agents.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from app.agents.orchestrator import agent_orchestration, AgentType

router = APIRouter(prefix="/api/v1/orchestration", tags=["agent-orchestration"])


class WorkflowTriggerRequest(BaseModel):
    """Request model for triggering agent workflows."""
    inventory_items: List[Dict[str, Any]] = Field(default_factory=list)
    sales_history: List[Dict[str, Any]] = Field(default_factory=list)
    suppliers: List[Dict[str, Any]] = Field(default_factory=list)
    seasonal_factors: Dict[str, Any] = Field(default_factory=dict)
    transactions: List[Dict[str, Any]] = Field(default_factory=list)
    regulations: List[Dict[str, Any]] = Field(default_factory=list)
    priority: str = "medium"
    workflow_type: str = "full_analysis"


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    workflow_id: str
    status: str
    stages: Dict[str, Any]
    final_decisions: List[Dict[str, Any]]
    timestamp: str
    execution_time_ms: Optional[int] = None
    error: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    agents: Dict[str, Dict[str, Any]]
    total_agents: int
    active_agents: int
    system_health: str


@router.post("/trigger-workflow", response_model=WorkflowResponse)
async def trigger_supply_chain_workflow(
    request: WorkflowTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    🚀 Trigger Complete Supply Chain Agent Workflow
    
    This endpoint implements your PlantUML diagram flow:
    1. Stock Monitoring Agent analyzes inventory
    2. Demand Forecasting predicts trends
    3. Vendor Negotiation finds best suppliers
    4. Financial Analysis calculates costs
    5. Compliance checks regulations
    6. Orchestrator makes final decisions
    """
    try:
        start_time = datetime.now()
        
        # Convert request to orchestrator format
        trigger_data = {
            "inventory_items": request.inventory_items,
            "sales_history": request.sales_history,
            "suppliers": request.suppliers,
            "seasonal_factors": request.seasonal_factors,
            "transactions": request.transactions,
            "regulations": request.regulations
        }
        
        # Execute complete workflow
        workflow_result = await agent_orchestration.trigger_workflow(trigger_data)
        
        end_time = datetime.now()
        execution_time = int((end_time - start_time).total_seconds() * 1000)
        
        # Add background task for notifications
        background_tasks.add_task(
            _send_workflow_notifications,
            workflow_result
        )
        
        return WorkflowResponse(
            workflow_id=workflow_result["workflow_id"],
            status="completed" if not workflow_result.get("error") else "failed",
            stages=workflow_result["stages"],
            final_decisions=workflow_result["final_decisions"],
            timestamp=workflow_result["timestamp"],
            execution_time_ms=execution_time,
            error=workflow_result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.get("/agents/status", response_model=AgentStatusResponse)
async def get_agent_system_status():
    """
    📊 Get Real-time Status of All AI Agents
    
    Returns status of:
    - Stock Monitoring Agent
    - Demand Forecasting Agent
    - Vendor Negotiation Agent
    - Finance & Tax Agent
    - Compliance Agent
    """
    try:
        agent_status = await agent_orchestration.get_agent_status()
        
        active_count = sum(1 for status in agent_status.values() 
                          if status["status"] == "active")
        
        system_health = "healthy" if active_count == len(agent_status) else "degraded"
        
        return AgentStatusResponse(
            agents=agent_status,
            total_agents=len(agent_status),
            active_agents=active_count,
            system_health=system_health
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/agents/{agent_type}/execute")
async def execute_single_agent_task(
    agent_type: str,
    task_data: Dict[str, Any]
):
    """
    🤖 Execute Task with Individual Agent
    
    Available agents:
    - stock_monitoring: Inventory analysis
    - demand_forecasting: Sales predictions
    - vendor_negotiation: Supplier optimization
    - finance_tax: Financial analysis
    - compliance: Regulatory checks
    """
    try:
        # Validate agent type
        try:
            agent_enum = AgentType(agent_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type. Available: {[e.value for e in AgentType]}"
            )
        
        # Get agent and execute task
        agent = agent_orchestration.orchestrator.agents.get(agent_enum)
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_type} not found"
            )
        
        result = await agent.execute_task(task_data)
        
        return {
            "agent_type": agent_type,
            "task_result": result,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    📋 Get Status of Specific Workflow
    """
    # This would typically query a database for workflow status
    # For now, return a mock response
    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "progress": 100,
        "current_stage": "completed",
        "results_available": True
    }


@router.post("/test-full-system")
async def test_complete_system():
    """
    🧪 Test Complete Agent System with Sample Data
    
    This endpoint demonstrates the full VeriChain workflow
    with realistic stationery supply chain data.
    """
    try:
        # Sample realistic data for stationery supply chain
        sample_data = WorkflowTriggerRequest(
            inventory_items=[
                {
                    "id": "BOOK_MATH_10",
                    "name": "Mathematics Textbook Grade 10",
                    "category": "educational_books",
                    "current_stock": 25,
                    "min_stock_level": 50,
                    "max_stock_level": 200,
                    "unit_price": 45.99,
                    "supplier": "Educational Publishers Ltd"
                },
                {
                    "id": "PEN_BLUE_PACK",
                    "name": "Blue Ballpoint Pens (Pack of 10)",
                    "category": "writing_instruments",
                    "current_stock": 80,
                    "min_stock_level": 100,
                    "max_stock_level": 500,
                    "unit_price": 12.99,
                    "supplier": "Writing Solutions Co"
                },
                {
                    "id": "NOTEBOOK_A4",
                    "name": "A4 Ruled Notebooks (200 pages)",
                    "category": "paper_products",
                    "current_stock": 30,
                    "min_stock_level": 75,
                    "max_stock_level": 400,
                    "unit_price": 15.50,
                    "supplier": "Paper Products Inc"
                }
            ],
            sales_history=[
                {"item_id": "BOOK_MATH_10", "quantity": 15, "date": "2025-09-15", "revenue": 689.85},
                {"item_id": "PEN_BLUE_PACK", "quantity": 25, "date": "2025-09-15", "revenue": 324.75},
                {"item_id": "NOTEBOOK_A4", "quantity": 12, "date": "2025-09-15", "revenue": 186.00},
                {"item_id": "BOOK_MATH_10", "quantity": 8, "date": "2025-09-14", "revenue": 367.92},
                {"item_id": "PEN_BLUE_PACK", "quantity": 18, "date": "2025-09-14", "revenue": 233.82}
            ],
            suppliers=[
                {
                    "id": "SUP_EDU_001",
                    "name": "Educational Publishers Ltd",
                    "category": "books",
                    "rating": 4.5,
                    "reliability_score": 0.92,
                    "avg_delivery_days": 7,
                    "payment_terms": "NET_30",
                    "contact": "orders@edupublishers.com"
                },
                {
                    "id": "SUP_OFFICE_002",
                    "name": "Writing Solutions Co",
                    "category": "stationery",
                    "rating": 4.2,
                    "reliability_score": 0.88,
                    "avg_delivery_days": 5,
                    "payment_terms": "NET_15",
                    "contact": "sales@writingsolutions.com"
                },
                {
                    "id": "SUP_PAPER_003",
                    "name": "Paper Products Inc",
                    "category": "paper",
                    "rating": 4.3,
                    "reliability_score": 0.90,
                    "avg_delivery_days": 6,
                    "payment_terms": "NET_20",
                    "contact": "orders@paperproducts.com"
                }
            ],
            seasonal_factors={
                "current_season": "back_to_school",
                "season_multiplier": 2.5,
                "upcoming_events": [
                    {"event": "mid_term_exams", "date": "2025-11-15", "impact": "high"},
                    {"event": "new_academic_year", "date": "2025-07-01", "impact": "very_high"}
                ],
                "academic_calendar": {
                    "school_start": "2025-07-01",
                    "first_term_end": "2025-09-30",
                    "exam_periods": ["2025-11-15", "2025-03-15"]
                }
            },
            transactions=[
                {"id": "TXN_001", "amount": 1250.50, "type": "purchase", "date": "2025-09-10"},
                {"id": "TXN_002", "amount": 890.25, "type": "purchase", "date": "2025-09-08"},
                {"id": "TXN_003", "amount": 2150.75, "type": "sale", "date": "2025-09-15"}
            ],
            regulations=[
                {"type": "safety", "requirement": "Child-safe materials", "compliance": True},
                {"type": "environmental", "requirement": "Eco-friendly packaging", "compliance": True},
                {"type": "quality", "requirement": "ISO 9001 certification", "compliance": True}
            ]
        )
        
        # Execute the workflow
        result = await trigger_supply_chain_workflow(sample_data, BackgroundTasks())
        
        return {
            "message": "Complete system test executed successfully",
            "workflow_result": result,
            "test_data_used": {
                "inventory_items_count": len(sample_data.inventory_items),
                "sales_records_count": len(sample_data.sales_history),
                "suppliers_count": len(sample_data.suppliers),
                "seasonal_factors_included": True,
                "compliance_checks_included": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"System test failed: {str(e)}"
        )


async def _send_workflow_notifications(workflow_result: Dict[str, Any]):
    """Background task to send notifications about workflow completion."""
    try:
        from app.services.notifications import notification_manager
        
        # Send notification about workflow completion
        await notification_manager.send_notification(
            title="Agent Workflow Completed",
            message=f"Workflow {workflow_result['workflow_id']} completed successfully",
            priority="medium"
        )
        
        # Send specific alerts based on decisions
        final_decisions = workflow_result.get("final_decisions", [])
        for decision in final_decisions:
            if "critical" in str(decision).lower():
                await notification_manager.send_notification(
                    title="Critical Supply Chain Decision Required",
                    message=f"Immediate action needed based on AI analysis",
                    priority="critical"
                )
                
    except Exception as e:
        # Log error but don't fail the workflow
        print(f"Failed to send workflow notifications: {e}")


# Additional utility endpoints

@router.get("/system/health")
async def get_orchestration_health():
    """Get overall orchestration system health."""
    try:
        agent_status = await agent_orchestration.get_agent_status()
        
        health_checks = {
            "agents_operational": all(
                status["status"] in ["active", "idle"] 
                for status in agent_status.values()
            ),
            "gemini_api_connected": True,  # Would check actual connectivity
            "database_accessible": True,   # Would check database
            "notification_system": True   # Would check notifications
        }
        
        overall_health = "healthy" if all(health_checks.values()) else "degraded"
        
        return {
            "status": overall_health,
            "timestamp": datetime.now().isoformat(),
            "checks": health_checks,
            "agent_count": len(agent_status),
            "version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }