"""
Advanced Auto-Ordering System with Stock Monitoring & Intelligent Triggers
Monitors inventory levels and automatically initiates orders when thresholds are reached.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random
from uuid import uuid4

from app.models.database import InventoryItemDB, AgentDecisionDB, AlertDB
from app.services.database import DatabaseManager
from app.services.ai_service import get_ai_service, VeriChainAIService
from app.services.notifications import notification_manager
from app.agents.stationery_agent import StationeryInventoryAgent
from app.models import SupplierInfo
from app.services.database import db_manager

class OrderPriority(Enum):
    EMERGENCY = "emergency"      # Out of stock
    URGENT = "urgent"           # Below 20% of minimum
    HIGH = "high"               # Below minimum threshold
    MEDIUM = "medium"           # Below 50% of max stock
    LOW = "low"                 # Seasonal preparation

class OrderStatus(Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class AutoOrderDecision:
    """Represents an automated ordering decision."""
    item_sku: str
    item_name: str
    current_stock: int
    minimum_stock: int
    recommended_quantity: int
    priority: OrderPriority
    estimated_cost: float
    supplier_id: Optional[str]
    supplier_name: Optional[str]
    reasoning: str
    confidence_score: float
    expected_delivery: datetime
    seasonal_factor: float
    created_at: datetime
    requires_approval: bool

@dataclass
class StockAlert:
    """Stock level alert with actionable information."""
    item_sku: str
    item_name: str
    current_stock: int
    threshold_type: str  # 'minimum', 'critical', 'out_of_stock'
    days_until_stockout: int
    auto_order_triggered: bool
    alert_level: OrderPriority
    message: str
    created_at: datetime

class AutoOrderingEngine:
    """Intelligent auto-ordering engine with stock monitoring."""
    
    def __init__(self, ai_service: VeriChainAIService = None):
        self.ai_service = ai_service
        self.stationery_agent = None  # Will initialize with AI service
        self.monitoring_active = False
        
        # Configuration
        self.config = {
            "check_interval_minutes": 30,  # Monitor every 30 minutes
            "emergency_threshold": 0,       # Out of stock
            "urgent_threshold": 0.2,        # 20% of minimum
            "auto_approve_threshold": 0.85, # Auto-approve if confidence > 85%
            "seasonal_buffer_days": 30,     # Look ahead for seasonal demands
            "max_order_value": 100000,      # Max auto-order value (₹)
        }
        
        # In-memory order tracking
        self.pending_orders: List[AutoOrderDecision] = []
        self.recent_alerts: List[StockAlert] = []
    
    async def start_monitoring(self):
        """Start continuous inventory monitoring."""
        self.monitoring_active = True
        print("🔄 Auto-ordering engine started - monitoring inventory levels...")
        
        while self.monitoring_active:
            try:
                await self.perform_stock_check()
                await asyncio.sleep(self.config["check_interval_minutes"] * 60)
            except Exception as e:
                print(f"❌ Error in monitoring cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def stop_monitoring(self):
        """Stop inventory monitoring."""
        self.monitoring_active = False
        print("⏹️ Auto-ordering engine stopped")
    
    async def perform_stock_check(self):
        """Perform comprehensive stock level analysis."""
        print("🔍 Performing automated stock check...")
        
        try:
            # Get all inventory items
            items = await db_manager.get_inventory_items(limit=1000)
            alerts_generated = 0
            orders_triggered = 0
            
            for item in items:
                # Analyze stock level
                alert = await self.analyze_stock_level(item)
                
                if alert:
                    self.recent_alerts.append(alert)
                    alerts_generated += 1
                    
                    # Trigger auto-order if needed
                    if alert.auto_order_triggered:
                        order_decision = await self.create_auto_order_decision(item, alert)
                        if order_decision:
                            await self.process_auto_order(order_decision)
                            orders_triggered += 1
            
            if alerts_generated > 0:
                print(f"⚠️ Generated {alerts_generated} stock alerts, triggered {orders_triggered} auto-orders")
                
                # Send summary notification to admin
                await self.send_monitoring_summary(alerts_generated, orders_triggered)
            
        except Exception as e:
            print(f"❌ Error in stock check: {e}")
    
    async def analyze_stock_level(self, item: InventoryItemDB) -> Optional[StockAlert]:
        """Analyze individual item stock level and determine alert type."""
        current_stock = item.current_stock
        minimum_stock = item.minimum_stock_level
        
        # Calculate stock ratios
        min_ratio = current_stock / minimum_stock if minimum_stock > 0 else 1.0
        
        # Determine alert type and priority
        alert_type = None
        priority = None
        auto_trigger = False
        
        if current_stock <= 0:
            alert_type = "out_of_stock"
            priority = OrderPriority.EMERGENCY
            auto_trigger = True
        elif current_stock < minimum_stock * self.config["urgent_threshold"]:
            alert_type = "critical"
            priority = OrderPriority.URGENT
            auto_trigger = True
        elif current_stock < minimum_stock:
            alert_type = "minimum"
            priority = OrderPriority.HIGH
            auto_trigger = True
        elif await self.check_seasonal_demand_surge(item):
            alert_type = "seasonal_prep"
            priority = OrderPriority.MEDIUM
            auto_trigger = False  # Requires manual approval
        
        if alert_type:
            # Calculate days until stockout
            days_until_stockout = await self.calculate_stockout_timeline(item)
            
            return StockAlert(
                item_sku=item.sku,
                item_name=item.name,
                current_stock=current_stock,
                threshold_type=alert_type,
                days_until_stockout=days_until_stockout,
                auto_order_triggered=auto_trigger,
                alert_level=priority,
                message=self.generate_alert_message(item, alert_type, days_until_stockout),
                created_at=datetime.utcnow()
            )
        
        return None

    async def check_seasonal_demand_surge(self, item: InventoryItemDB) -> bool:
        """Check if item is approaching seasonal demand surge."""
        current_month = datetime.now().month
        next_month = (current_month % 12) + 1
        
        # Get seasonal patterns from the agent
        category_patterns = {
            "WRITING_INSTRUMENTS": [6, 7, 11, 12],  # Peak months
            "PAPER_NOTEBOOKS": [6, 7],
            "ART_CRAFT": [10, 11, 12],  # Festival season
            "BAGS_STORAGE": [5, 6, 7],  # School preparation
        }
        
        peak_months = category_patterns.get(item.category, [])
        
        # Check if next month is a peak month
        return next_month in peak_months
    
    async def calculate_stockout_timeline(self, item:InventoryItemDB) -> int:
        """Calculate days until item will be out of stock."""
        # Get recent sales data to calculate average daily consumption
        sales_data = await db_manager.get_sales_data(
            sku=item.sku,
            days=30  # Last 30 days
        )
        
        if not sales_data:
            return 999  # Unknown consumption rate
        
        # Calculate average daily consumption
        total_sold = sum(sale.quantity_sold for sale in sales_data)
        avg_daily_consumption = total_sold / 30
        
        if avg_daily_consumption <= 0:
            return 999  # No consumption
        
        # Days until stockout
        days_remaining = item.current_stock / avg_daily_consumption
        return max(0, int(days_remaining))
    
    async def create_auto_order_decision(self, item: InventoryItemDB, alert: StockAlert) -> Optional[AutoOrderDecision]:
        """Create intelligent auto-order decision."""
        try:
            # Find best supplier for this item
            supplier = await self.find_best_supplier(item)
            
            if not supplier:
                print(f"⚠️ No supplier found for {item.sku}")
                return None
            
            # Calculate optimal order quantity using AI agent
            order_analysis = await self.stationery_agent.analyze_seasonal_demand(
                item, 
                await db_manager.get_sales_data(item.sku, days=90),
                datetime.now().month
            )
            
            # Determine order quantity based on analysis
            recommended_quantity = self.calculate_order_quantity(item, alert, order_analysis)
            
            # Calculate costs
            unit_cost = item.unit_cost
            estimated_cost = recommended_quantity * unit_cost
            
            # Apply supplier discount
            if supplier.discount_rate > 0:
                estimated_cost *= (1 - supplier.discount_rate / 100)
            
            # Calculate confidence score
            confidence = self.calculate_order_confidence(item, alert, order_analysis, supplier)
            
            # Determine if approval is needed
            requires_approval = (
                estimated_cost > self.config["max_order_value"] or
                confidence < self.config["auto_approve_threshold"] or
                alert.alert_level in [OrderPriority.EMERGENCY, OrderPriority.URGENT]
            )
            
            return AutoOrderDecision(
                item_sku=item.sku,
                item_name=item.name,
                current_stock=item.current_stock,
                minimum_stock=item.minimum_stock_level,
                recommended_quantity=recommended_quantity,
                priority=alert.alert_level,
                estimated_cost=estimated_cost,
                supplier_id=str(supplier.id),
                supplier_name=supplier.name,
                reasoning=self.generate_order_reasoning(item, alert, order_analysis, supplier),
                confidence_score=confidence,
                expected_delivery=datetime.utcnow() + timedelta(days=supplier.delivery_time_days),
                seasonal_factor=order_analysis.get("seasonal_multiplier", 1.0),
                created_at=datetime.utcnow(),
                requires_approval=requires_approval
            )
            
        except Exception as e:
            print(f"❌ Error creating auto-order decision for {item.sku}: {e}")
            return None
    
    def calculate_order_quantity(self, item: InventoryItemDB, alert: StockAlert, analysis: Dict) -> int:
        """Calculate optimal order quantity."""
        # Base quantity to reach maximum stock
        base_quantity = item.maximum_stock_level - item.current_stock
        
        # Apply seasonal adjustment
        seasonal_multiplier = analysis.get("seasonal_multiplier", 1.0)
        seasonal_quantity = int(base_quantity * seasonal_multiplier)
        
        # Apply urgency multiplier
        urgency_multipliers = {
            OrderPriority.EMERGENCY: 1.5,  # Emergency stock
            OrderPriority.URGENT: 1.3,
            OrderPriority.HIGH: 1.1,
            OrderPriority.MEDIUM: 1.0,
            OrderPriority.LOW: 0.8
        }
        
        urgency_multiplier = urgency_multipliers.get(alert.alert_level, 1.0)
        final_quantity = int(seasonal_quantity * urgency_multiplier)
        
        # Ensure minimum order (supplier might have MOQ)
        final_quantity = max(final_quantity, 100)  # Minimum 100 units
        
        # Cap at reasonable maximum
        final_quantity = min(final_quantity, item.maximum_stock_level * 2)
        
        return final_quantity
    
    def calculate_order_confidence(self, item: InventoryItemDB, alert: StockAlert,
                                 analysis: Dict, supplier: Dict) -> float:
        """Calculate confidence score for auto-order decision."""
        confidence = 0.7  # Base confidence
        
        # Stock level factor
        if alert.alert_level == OrderPriority.EMERGENCY:
            confidence += 0.2  # High confidence for emergency
        elif alert.alert_level == OrderPriority.URGENT:
            confidence += 0.15
        
        # Supplier reliability factor
        if supplier.rating >= 4.5:
            confidence += 0.1
        elif supplier.rating >= 4.0:
            confidence += 0.05
        
        # Historical data factor
        if analysis.get("data_points", 0) > 30:
            confidence += 0.1
        
        # Seasonal certainty
        if analysis.get("seasonal_confidence", 0) > 0.8:
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%
    
    async def find_best_supplier(self, item: InventoryItemDB) -> Optional[SupplierInfo]:
        """Find the best supplier for an item based on multiple factors."""
        # Get all suppliers that handle this category
        suppliers = await db_manager.get_suppliers_by_category(item.category)
        
        if not suppliers:
            return None
        
        # Score suppliers based on multiple factors
        best_supplier = None
        best_score = 0
        
        for supplier in suppliers:
            score = 0
            
            # Rating factor (40%)
            score += (supplier.rating / 5.0) * 0.4
            
            # Discount factor (25%)
            score += (supplier.discount_rate / 20.0) * 0.25  # Normalize discount
            
            # Delivery speed factor (20%)
            delivery_score = max(0, 1 - (supplier.delivery_time_days / 10.0))
            score += delivery_score * 0.2
            
            # Payment terms factor (15%)
            payment_terms_score = 0.7  # Base score
            if "Net 15" in supplier.payment_terms:
                payment_terms_score = 0.9
            elif "Net 30" in supplier.payment_terms:
                payment_terms_score = 0.8
            elif "Net 60" in supplier.payment_terms:
                payment_terms_score = 0.6
            score += payment_terms_score * 0.15
            
            if score > best_score:
                best_score = score
                best_supplier = supplier
        
        return best_supplier
    
    async def process_auto_order(self, decision: AutoOrderDecision):
        """Process an auto-order decision."""
        try:
            if decision.requires_approval:
                # Add to pending orders and notify admin
                self.pending_orders.append(decision)
                await self.notify_admin_for_approval(decision)
                print(f"📋 Auto-order for {decision.item_sku} added to approval queue")
            else:
                # Auto-approve and execute
                await self.execute_auto_order(decision)
                print(f"✅ Auto-order for {decision.item_sku} executed automatically")
            
            # Save decision to database
            await self.save_order_decision(decision)
            
        except Exception as e:
            print(f"❌ Error processing auto-order for {decision.item_sku}: {e}")
    
    async def execute_auto_order(self, decision: AutoOrderDecision):
        """Execute an approved auto-order."""
        # Create agent decision record
        agent_decision = AgentDecisionDB(
            id=uuid4(),
            agent_role="AutoOrderingEngine",
            item_sku=decision.item_sku,
            action_type="AUTO_RESTOCK",
            confidence_score=decision.confidence_score,
            reasoning=decision.reasoning,
            recommended_quantity=decision.recommended_quantity,
            estimated_cost=decision.estimated_cost,
            priority=decision.priority.value,
            approved=True,
            executed=True,
            created_at=decision.created_at,
            approved_at=datetime.utcnow()
        )
        
        # Save to database
        await db_manager.save_agent_decision(agent_decision)
        
        # Send order to supplier (mock implementation)
        await self.send_order_to_supplier(decision)
        
        # Update inventory (simulated)
        await self.update_inventory_for_order(decision)
        
        # Notify relevant stakeholders
        await self.notify_order_executed(decision)
    
    async def send_order_to_supplier(self, decision: AutoOrderDecision):
        """Send order to supplier (mock implementation)."""
        # In real implementation, this would integrate with supplier APIs/email
        order_data = {
            "order_id": str(uuid4()),
            "supplier": decision.supplier_name,
            "item_sku": decision.item_sku,
            "item_name": decision.item_name,
            "quantity": decision.recommended_quantity,
            "estimated_cost": decision.estimated_cost,
            "expected_delivery": decision.expected_delivery.isoformat(),
            "priority": decision.priority.value
        }
        
        print(f"📤 Mock order sent to {decision.supplier_name}: {order_data}")
        
        # Create mock order confirmation
        await notification_manager.send_notification(
            type="order_sent",
            title=f"Order Sent: {decision.item_name}",
            message=f"Purchase order sent to {decision.supplier_name} for {decision.recommended_quantity} units",
            recipient="procurement@verichain.com"
        )
    
    async def update_inventory_for_order(self, decision: AutoOrderDecision):
        """Update inventory to reflect incoming order."""
        # Mark as "on order" in the system
        # In real implementation, this would update the item's pending_stock field
        print(f"📦 Inventory updated: {decision.recommended_quantity} units of {decision.item_sku} on order")
    
    def generate_alert_message(self, item: InventoryItemDB, alert_type: str, days_until_stockout: int) -> str:
        """Generate user-friendly alert message."""
        if alert_type == "out_of_stock":
            return f"🚨 CRITICAL: {item.name} is completely out of stock! Auto-order initiated."
        elif alert_type == "critical":
            return f"⚠️ URGENT: {item.name} stock critically low ({item.current_stock} units). Estimated {days_until_stockout} days until stockout."
        elif alert_type == "minimum":
            return f"📉 {item.name} below minimum stock level ({item.current_stock}/{item.minimum_stock_level}). Auto-order triggered."
        elif alert_type == "seasonal_prep":
            return f"📈 Seasonal demand surge expected for {item.name}. Consider increasing stock levels."
        else:
            return f"Stock alert for {item.name}: {alert_type}"
    
    def generate_order_reasoning(self, item: InventoryItemDB, alert: StockAlert, 
                               analysis: Dict, supplier: SupplierInfo) -> str:
        """Generate detailed reasoning for order decision."""
        reasoning_parts = [
            f"Stock Level Analysis: Current stock ({item.current_stock}) is {alert.threshold_type}",
            f"Demand Forecast: {analysis.get('prediction_summary', 'Based on historical patterns')}",
            f"Supplier Selection: {supplier.name} chosen for {supplier.rating}/5 rating and {supplier.discount_rate}% discount",
            f"Delivery Timeline: {supplier.delivery_time_days} days expected delivery",
            f"Seasonal Factor: {analysis.get('seasonal_multiplier', 1.0):.2f}x multiplier applied"
        ]
        
        if alert.days_until_stockout < 7:
            reasoning_parts.append(f"URGENT: Only {alert.days_until_stockout} days until stockout")
        
        return "; ".join(reasoning_parts)
    
    async def notify_admin_for_approval(self, decision: AutoOrderDecision):
        """Notify admin about pending order approval."""
        await notification_manager.send_notification(
            type="order_approval_required",
            title=f"Order Approval Required: {decision.item_name}",
            message=f"Auto-order for {decision.recommended_quantity} units (₹{decision.estimated_cost:,.2f}) requires approval. Priority: {decision.priority.value}",
            recipient="admin@verichain.com",
            action_required=True,
            metadata={
                "order_id": decision.item_sku,
                "approval_url": f"/dashboard/orders/approve/{decision.item_sku}"
            }
        )
    
    async def notify_order_executed(self, decision: AutoOrderDecision):
        """Notify about executed order."""
        await notification_manager.send_notification(
            type="order_executed",
            title=f"Order Executed: {decision.item_name}",
            message=f"Auto-order completed for {decision.recommended_quantity} units from {decision.supplier_name}. Expected delivery: {decision.expected_delivery.strftime('%Y-%m-%d')}",
            recipient="inventory@verichain.com"
        )
    
    async def send_monitoring_summary(self, alerts_count: int, orders_count: int):
        """Send monitoring summary to admin."""
        if alerts_count > 0:
            await notification_manager.send_notification(
                type="monitoring_summary",
                title="Inventory Monitoring Summary",
                message=f"Stock check completed: {alerts_count} alerts generated, {orders_count} auto-orders triggered",
                recipient="admin@verichain.com"
            )
    
    async def save_order_decision(self, decision: AutoOrderDecision):
        """Save order decision to database."""
        agent_decision = AgentDecisionDB(
            id=uuid4(),
            agent_role="AutoOrderingEngine",
            item_sku=decision.item_sku,
            action_type="AUTO_ORDER_DECISION",
            confidence_score=decision.confidence_score,
            reasoning=decision.reasoning,
            recommended_quantity=decision.recommended_quantity,
            estimated_cost=decision.estimated_cost,
            priority=decision.priority.value,
            approved=not decision.requires_approval,
            executed=False,
            created_at=decision.created_at
        )
        
        await db_manager.save_agent_decision(agent_decision)
    
    # API Methods for Dashboard Integration
    
    async def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending order approvals."""
        return [
            {
                "item_sku": order.item_sku,
                "item_name": order.item_name,
                "quantity": order.recommended_quantity,
                "cost": order.estimated_cost,
                "supplier": order.supplier_name,
                "priority": order.priority.value,
                "confidence": order.confidence_score,
                "reasoning": order.reasoning,
                "created_at": order.created_at.isoformat()
            }
            for order in self.pending_orders
        ]
    
    async def approve_order(self, item_sku: str, admin_user: str) -> bool:
        """Approve a pending order."""
        for i, order in enumerate(self.pending_orders):
            if order.item_sku == item_sku:
                # Execute the order
                await self.execute_auto_order(order)
                
                # Remove from pending
                self.pending_orders.pop(i)
                
                # Log approval
                await notification_manager.send_notification(
                    type="order_approved",
                    title=f"Order Approved: {order.item_name}",
                    message=f"Order approved by {admin_user} and executed",
                    recipient="procurement@verichain.com"
                )
                
                return True
        
        return False
    
    async def reject_order(self, item_sku: str, admin_user: str, reason: str) -> bool:
        """Reject a pending order."""
        for i, order in enumerate(self.pending_orders):
            if order.item_sku == item_sku:
                # Remove from pending
                self.pending_orders.pop(i)
                
                # Log rejection
                await notification_manager.send_notification(
                    type="order_rejected",
                    title=f"Order Rejected: {order.item_name}",
                    message=f"Order rejected by {admin_user}. Reason: {reason}",
                    recipient="procurement@verichain.com"
                )
                
                return True
        
        return False
    
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent stock alerts."""
        recent = sorted(self.recent_alerts, key=lambda x: x.created_at, reverse=True)[:limit]
        
        return [
            {
                "item_sku": alert.item_sku,
                "item_name": alert.item_name,
                "current_stock": alert.current_stock,
                "threshold_type": alert.threshold_type,
                "days_until_stockout": alert.days_until_stockout,
                "auto_order_triggered": alert.auto_order_triggered,
                "alert_level": alert.alert_level.value,
                "message": alert.message,
                "created_at": alert.created_at.isoformat()
            }
            for alert in recent
        ]

# Global auto-ordering engine instance
auto_ordering_engine = None

async def initialize_auto_ordering():
    """Initialize the auto-ordering engine with AI service."""
    global auto_ordering_engine
    ai_service = await get_ai_service()
    auto_ordering_engine = AutoOrderingEngine(ai_service)
    
    # Start monitoring in background
    asyncio.create_task(auto_ordering_engine.start_monitoring())
    
    print("🚀 Auto-ordering engine initialized with AI and monitoring started")

async def get_auto_ordering_engine() -> AutoOrderingEngine:
    """Get the auto-ordering engine instance."""
    if auto_ordering_engine is None:
        await initialize_auto_ordering()
    return auto_ordering_engine