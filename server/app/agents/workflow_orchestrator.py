import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.supply_chain_agent import SupplyChainAgent
from app.services.database import (
    InventoryService, SalesService, VendorService, OrderService, AgentDecisionService
)
from app.services.analysis_engine import (
    StockAnalyzer, SalesTrendAnalyzer, AnomalyDetector, 
    DemandForecaster, VendorAnalyzer, AnalysisResult
)
from app.models import AgentDecisionType, OrderStatus
from app.core.logging import logger


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(Enum):
    DATA_FETCH = "data_fetch"
    ANALYSIS = "analysis"
    AI_REASONING = "ai_reasoning"
    DECISION_MAKING = "decision_making"
    ACTION_EXECUTION = "action_execution"
    LOGGING = "logging"


@dataclass
class WorkflowContext:
    """Context object passed through workflow steps"""
    workflow_id: str
    trigger_type: str
    parameters: Dict[str, Any]
    status: WorkflowStatus
    current_step: Optional[WorkflowStep]
    data: Dict[str, Any]
    results: Dict[str, Any]
    decisions: List[Dict[str, Any]]
    actions_taken: List[Dict[str, Any]]
    errors: List[str]
    started_at: datetime
    completed_at: Optional[datetime]


class AgentWorkflowOrchestrator:
    """Orchestrates the complete agentic workflow pipeline"""
    
    def __init__(self):
        self.agent = SupplyChainAgent()
        self.active_workflows: Dict[str, WorkflowContext] = {}
        
    async def trigger_full_analysis(
        self, 
        db: AsyncSession,
        trigger_type: str = "scheduled",
        parameters: Optional[Dict[str, Any]] = None
    ) -> WorkflowContext:
        """Trigger a complete supply chain analysis workflow"""
        
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
        
        context = WorkflowContext(
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            parameters=parameters or {},
            status=WorkflowStatus.PENDING,
            current_step=None,
            data={},
            results={},
            decisions=[],
            actions_taken=[],
            errors=[],
            started_at=datetime.utcnow(),
            completed_at=None
        )
        
        self.active_workflows[workflow_id] = context
        
        try:
            context.status = WorkflowStatus.RUNNING
            
            # Step 1: Data Fetch
            await self._execute_data_fetch_step(db, context)
            
            # Step 2: Analysis
            await self._execute_analysis_step(context)
            
            # Step 3: AI Reasoning
            await self._execute_ai_reasoning_step(context)
            
            # Step 4: Decision Making
            await self._execute_decision_making_step(context)
            
            # Step 5: Action Execution
            await self._execute_action_execution_step(db, context)
            
            # Step 6: Logging
            await self._execute_logging_step(db, context)
            
            context.status = WorkflowStatus.COMPLETED
            context.completed_at = datetime.utcnow()
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.errors.append(f"Workflow failed: {str(e)}")
            context.completed_at = datetime.utcnow()
            
            logger.error(f"Workflow {workflow_id} failed: {str(e)}", exc_info=True)
        
        return context
    
    async def _execute_data_fetch_step(self, db: AsyncSession, context: WorkflowContext):
        """Step 1: Fetch all necessary data"""
        context.current_step = WorkflowStep.DATA_FETCH
        
        try:
            # Fetch inventory data
            inventory_items = await InventoryService.get_all_items(db)
            context.data["inventory"] = [
                {
                    "id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "category": item.category.value,
                    "current_stock": item.current_stock,
                    "reorder_level": item.reorder_level,
                    "max_stock_level": item.max_stock_level,
                    "unit_cost": item.unit_cost,
                    "updated_at": item.updated_at.isoformat()
                }
                for item in inventory_items
            ]
            
            # Fetch recent sales data (last 30 days)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            sales_records = await SalesService.get_sales_by_period(db, start_date, end_date)
            context.data["sales"] = [
                {
                    "id": sale.id,
                    "item_id": sale.item_id,
                    "quantity_sold": sale.quantity_sold,
                    "unit_price": sale.unit_price,
                    "total_amount": sale.total_amount,
                    "sale_date": sale.sale_date.isoformat(),
                    "department": sale.department
                }
                for sale in sales_records
            ]
            
            # Fetch vendor data
            vendors = await VendorService.get_all_vendors(db)
            context.data["vendors"] = [
                {
                    "id": vendor.id,
                    "name": vendor.name,
                    "status": vendor.status.value,
                    "reliability_score": vendor.reliability_score,
                    "avg_delivery_days": vendor.avg_delivery_days,
                    "contact_person": vendor.contact_person,
                    "email": vendor.email
                }
                for vendor in vendors
            ]
            
            # Fetch pending orders
            pending_orders = await OrderService.get_pending_orders(db)
            context.data["pending_orders"] = [
                {
                    "id": order.id,
                    "order_number": order.order_number,
                    "vendor_id": order.vendor_id,
                    "total_amount": order.total_amount,
                    "order_date": order.order_date.isoformat(),
                    "expected_delivery_date": order.expected_delivery_date.isoformat() if order.expected_delivery_date else None
                }
                for order in pending_orders
            ]
            
            logger.info(f"Data fetch completed: {len(inventory_items)} items, {len(sales_records)} sales, {len(vendors)} vendors")
            
        except Exception as e:
            context.errors.append(f"Data fetch failed: {str(e)}")
            raise
    
    async def _execute_analysis_step(self, context: WorkflowContext):
        """Step 2: Perform statistical analysis"""
        context.current_step = WorkflowStep.ANALYSIS
        
        try:
            analysis_results = {}
            
            # Stock level analysis
            stock_analysis = StockAnalyzer.analyze_stock_status(context.data["inventory"])
            analysis_results["stock_analysis"] = asdict(stock_analysis)
            
            # Sales trend analysis
            sales_trend = SalesTrendAnalyzer.analyze_sales_trends(context.data["sales"])
            analysis_results["sales_trends"] = asdict(sales_trend)
            
            # Anomaly detection
            anomaly_results = AnomalyDetector.detect_sales_anomalies(context.data["sales"])
            analysis_results["anomalies"] = asdict(anomaly_results)
            
            # Vendor performance analysis
            vendor_analysis = VendorAnalyzer.analyze_vendor_performance(context.data["vendors"])
            analysis_results["vendor_performance"] = asdict(vendor_analysis)
            
            # Item-specific demand forecasting for critical items
            critical_items = stock_analysis.data.get("critical_items", [])
            forecasts = {}
            for item in critical_items[:5]:  # Limit to top 5 critical items
                item_sales = [s for s in context.data["sales"] if s["item_id"] == item["id"]]
                forecast = DemandForecaster.forecast_demand(item_sales, item["id"])
                forecasts[item["id"]] = asdict(forecast)
            
            analysis_results["demand_forecasts"] = forecasts
            
            context.results["analysis"] = analysis_results
            
            logger.info(f"Analysis completed: {len(critical_items)} critical items, {len(forecasts)} forecasts")
            
        except Exception as e:
            context.errors.append(f"Analysis failed: {str(e)}")
            raise
    
    async def _execute_ai_reasoning_step(self, context: WorkflowContext):
        """Step 3: AI agent reasoning and recommendations"""
        context.current_step = WorkflowStep.AI_REASONING
        
        try:
            # Prepare data for AI agent
            ai_response = await self.agent.analyze_inventory_situation(
                inventory_data=context.data["inventory"],
                sales_data=context.data["sales"],
                vendor_data=context.data["vendors"],
                context=context.results.get("analysis", {})
            )
            
            context.results["ai_analysis"] = ai_response
            
            if ai_response["success"]:
                logger.info(f"AI analysis completed with confidence: {ai_response.get('confidence', 0)}")
            else:
                context.errors.append(f"AI analysis failed: {ai_response.get('error', 'Unknown error')}")
            
        except Exception as e:
            context.errors.append(f"AI reasoning failed: {str(e)}")
            raise
    
    async def _execute_decision_making_step(self, context: WorkflowContext):
        """Step 4: Convert analysis into actionable decisions"""
        context.current_step = WorkflowStep.DECISION_MAKING
        
        try:
            decisions = []
            
            ai_analysis = context.results.get("ai_analysis", {})
            if ai_analysis.get("success"):
                analysis_data = ai_analysis.get("analysis", {})
                
                # Reorder decisions
                restock_recommendations = analysis_data.get("restock_recommendations", [])
                for recommendation in restock_recommendations:
                    decision = {
                        "type": "reorder",
                        "item_id": recommendation.get("item_id"),
                        "recommended_quantity": recommendation.get("recommended_quantity"),
                        "priority": recommendation.get("priority"),
                        "reasoning": recommendation.get("reasoning"),
                        "confidence": ai_analysis.get("confidence", 0.5),
                        "estimated_cost": recommendation.get("recommended_quantity", 0) * 10,  # Estimate
                        "created_at": datetime.utcnow().isoformat()
                    }
                    decisions.append(decision)
                
                # Alert decisions
                anomaly_alerts = analysis_data.get("anomaly_alerts", [])
                for alert in anomaly_alerts:
                    decision = {
                        "type": "alert",
                        "item_id": alert.get("item_id"),
                        "alert_type": alert.get("type"),
                        "severity": alert.get("severity"),
                        "description": alert.get("description"),
                        "action_required": alert.get("action_required"),
                        "confidence": 0.8,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    decisions.append(decision)
                
                # Vendor risk decisions
                vendor_risks = analysis_data.get("vendor_risks", [])
                for risk in vendor_risks:
                    decision = {
                        "type": "vendor_risk",
                        "vendor_id": risk.get("vendor_id"),
                        "risk_type": risk.get("risk_type"),
                        "impact": risk.get("impact"),
                        "mitigation": risk.get("mitigation"),
                        "confidence": 0.7,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    decisions.append(decision)
            
            # Add decisions from statistical analysis
            stock_analysis = context.results.get("analysis", {}).get("stock_analysis", {})
            stock_alerts = stock_analysis.get("alerts", [])
            for alert in stock_alerts:
                decision = {
                    "type": "stock_alert",
                    "item_id": alert.get("item_id"),
                    "severity": alert.get("severity"),
                    "message": alert.get("message"),
                    "confidence": 0.9,
                    "created_at": datetime.utcnow().isoformat()
                }
                decisions.append(decision)
            
            context.decisions = decisions
            
            logger.info(f"Decision making completed: {len(decisions)} decisions generated")
            
        except Exception as e:
            context.errors.append(f"Decision making failed: {str(e)}")
            raise
    
    async def _execute_action_execution_step(self, db: AsyncSession, context: WorkflowContext):
        """Step 5: Execute approved actions"""
        context.current_step = WorkflowStep.ACTION_EXECUTION
        
        try:
            actions_taken = []
            
            # Auto-execute low-risk actions
            for decision in context.decisions:
                action = None
                
                if decision["type"] == "reorder" and decision.get("priority") == "high":
                    # Auto-create orders for high-priority items
                    if decision.get("confidence", 0) > 0.7:
                        action = await self._create_reorder_action(db, decision)
                        if action:
                            actions_taken.append(action)
                
                elif decision["type"] in ["alert", "stock_alert"]:
                    # Log alerts for human review
                    action = await self._create_alert_action(db, decision)
                    if action:
                        actions_taken.append(action)
                
                elif decision["type"] == "vendor_risk":
                    # Flag vendor for review
                    action = await self._create_vendor_review_action(db, decision)
                    if action:
                        actions_taken.append(action)
            
            context.actions_taken = actions_taken
            
            logger.info(f"Action execution completed: {len(actions_taken)} actions taken")
            
        except Exception as e:
            context.errors.append(f"Action execution failed: {str(e)}")
            raise
    
    async def _execute_logging_step(self, db: AsyncSession, context: WorkflowContext):
        """Step 6: Log all decisions and actions"""
        context.current_step = WorkflowStep.LOGGING
        
        try:
            # Log each decision
            for decision in context.decisions:
                decision_type = AgentDecisionType.REORDER
                if decision["type"] == "alert":
                    decision_type = AgentDecisionType.ALERT
                elif decision["type"] == "vendor_risk":
                    decision_type = AgentDecisionType.VENDOR_RISK
                elif decision["type"] == "stock_alert":
                    decision_type = AgentDecisionType.ALERT
                
                await AgentDecisionService.log_decision(
                    db=db,
                    decision_type=decision_type,
                    decision_data=decision,
                    reasoning=decision.get("reasoning", decision.get("message", "Auto-generated decision")),
                    confidence_score=decision.get("confidence", 0.5),
                    item_id=decision.get("item_id"),
                    vendor_id=decision.get("vendor_id")
                )
            
            # Log workflow summary
            workflow_summary = {
                "workflow_id": context.workflow_id,
                "trigger_type": context.trigger_type,
                "total_decisions": len(context.decisions),
                "actions_taken": len(context.actions_taken),
                "errors": len(context.errors),
                "duration_seconds": (datetime.utcnow() - context.started_at).total_seconds(),
                "status": context.status.value
            }
            
            await AgentDecisionService.log_decision(
                db=db,
                decision_type=AgentDecisionType.ALERT,
                decision_data=workflow_summary,
                reasoning=f"Workflow {context.workflow_id} completed",
                confidence_score=1.0 if context.status == WorkflowStatus.COMPLETED else 0.5
            )
            
            logger.info(f"Logging completed for workflow {context.workflow_id}")
            
        except Exception as e:
            context.errors.append(f"Logging failed: {str(e)}")
            raise
    
    async def _create_reorder_action(self, db: AsyncSession, decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a reorder action through AI agent negotiation"""
        try:
            item_id = decision.get("item_id")
            quantity = decision.get("recommended_quantity", 10)
            
            # Get item details
            item = await InventoryService.get_item(db, item_id)
            if not item:
                return {
                    "type": "reorder_failed",
                    "reason": "Item not found",
                    "item_id": item_id
                }
            
            # Start AI agent negotiation instead of direct order creation
            from ..api.ai_agent import start_negotiation_background
            
            negotiation_data = {
                "item_id": item_id,
                "quantity_needed": quantity,
                "urgency": "high" if decision.get("confidence", 0) > 0.8 else "medium",
                "trigger_source": "auto_refill",
                "auto_decision_data": decision
            }
            
            # Start background negotiation process
            session_id = await start_negotiation_background(db, negotiation_data)
            
            return {
                "type": "negotiation_started", 
                "session_id": session_id,
                "item_id": item_id,
                "item_name": item.name,
                "quantity": quantity,
                "trigger": "auto_refill",
                "confidence": decision.get("confidence", 0),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create reorder action: {str(e)}")
            return {
                "type": "reorder_failed",
                "reason": f"Error starting negotiation: {str(e)}",
                "item_id": item_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create reorder action: {str(e)}")
            return {
                "type": "reorder_failed",
                "reason": str(e),
                "item_id": decision.get("item_id")
            }
    
    async def _create_alert_action(self, db: AsyncSession, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert action"""
        return {
            "type": "alert_logged",
            "alert_type": decision.get("alert_type", decision.get("type")),
            "item_id": decision.get("item_id"),
            "severity": decision.get("severity"),
            "message": decision.get("message", decision.get("description")),
            "requires_human_review": True,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _create_vendor_review_action(self, db: AsyncSession, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Create a vendor review action"""
        return {
            "type": "vendor_review_flagged",
            "vendor_id": decision.get("vendor_id"),
            "risk_type": decision.get("risk_type"),
            "impact": decision.get("impact"),
            "mitigation": decision.get("mitigation"),
            "requires_human_review": True,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        if workflow_id not in self.active_workflows:
            return None
        
        context = self.active_workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": context.status.value,
            "current_step": context.current_step.value if context.current_step else None,
            "progress": self._calculate_progress(context),
            "decisions_count": len(context.decisions),
            "actions_count": len(context.actions_taken),
            "errors_count": len(context.errors),
            "started_at": context.started_at.isoformat(),
            "completed_at": context.completed_at.isoformat() if context.completed_at else None
        }
    
    def _calculate_progress(self, context: WorkflowContext) -> float:
        """Calculate workflow progress percentage"""
        if context.status == WorkflowStatus.COMPLETED:
            return 100.0
        elif context.status == WorkflowStatus.FAILED:
            return 0.0 if not context.current_step else 50.0
        
        step_weights = {
            WorkflowStep.DATA_FETCH: 20,
            WorkflowStep.ANALYSIS: 30,
            WorkflowStep.AI_REASONING: 40,
            WorkflowStep.DECISION_MAKING: 60,
            WorkflowStep.ACTION_EXECUTION: 80,
            WorkflowStep.LOGGING: 95
        }
        
        return step_weights.get(context.current_step, 0)
    
    async def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up old completed workflows"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        workflows_to_remove = []
        for workflow_id, context in self.active_workflows.items():
            if (context.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] and 
                context.completed_at and context.completed_at < cutoff_time):
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.active_workflows[workflow_id]
        
        logger.info(f"Cleaned up {len(workflows_to_remove)} old workflows")