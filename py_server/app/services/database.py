"""
Database operations and persistence layer.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from databases import Database

from app.core.config import settings
from app.models.database import Base, InventoryItemDB, SalesDataDB, AgentDecisionDB, AlertDB
from app.models import InventoryItem, SalesData, AgentDecision, Alert


class DatabaseManager:
    """
    Database manager for VeriChain application.
    """
    
    def __init__(self):
        self.database_url = settings.get_database_url()
        self.engine = create_engine(self.database_url)
        self.database = Database(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    async def connect(self):
        """Connect to the database."""
        await self.database.connect()
    
    async def disconnect(self):
        """Disconnect from the database."""
        await self.database.disconnect()
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    # Inventory Items
    async def save_inventory_item(self, item: InventoryItem) -> InventoryItemDB:
        """Save inventory item to database."""
        query = """
        INSERT INTO inventory_items (id, sku, name, category, current_stock, min_stock_threshold, 
                                   max_stock_capacity, unit_cost, supplier_id, location, status, 
                                   lead_time_days, created_at, updated_at)
        VALUES (:id, :sku, :name, :category, :current_stock, :min_stock_threshold, 
                :max_stock_capacity, :unit_cost, :supplier_id, :location, :status, 
                :lead_time_days, :created_at, :updated_at)
        ON CONFLICT(sku) DO UPDATE SET
            current_stock = :current_stock,
            min_stock_threshold = :min_stock_threshold,
            max_stock_capacity = :max_stock_capacity,
            unit_cost = :unit_cost,
            supplier_id = :supplier_id,
            location = :location,
            status = :status,
            lead_time_days = :lead_time_days,
            updated_at = :updated_at
        """
        
        values = {
            "id": item.id,
            "sku": item.sku,
            "name": item.name,
            "category": item.category,
            "current_stock": item.current_stock,
            "min_stock_threshold": item.min_stock_threshold,
            "max_stock_capacity": item.max_stock_capacity,
            "unit_cost": item.unit_cost,
            "supplier_id": item.supplier_id,
            "location": item.location,
            "status": item.status.value,
            "lead_time_days": item.lead_time_days,
            "created_at": item.created_at,
            "updated_at": item.updated_at
        }
        
        await self.database.execute(query, values)
        return item
    
    async def get_inventory_items(self, limit: int = 100) -> List[InventoryItem]:
        """Get inventory items from database."""
        query = "SELECT * FROM inventory_items ORDER BY updated_at DESC LIMIT :limit"
        rows = await self.database.fetch_all(query, {"limit": limit})
        
        items = []
        for row in rows:
            item = InventoryItem(
                id=row["id"],
                sku=row["sku"],
                name=row["name"],
                category=row["category"],
                current_stock=row["current_stock"],
                min_stock_threshold=row["min_stock_threshold"],
                max_stock_capacity=row["max_stock_capacity"],
                unit_cost=row["unit_cost"],
                supplier_id=row["supplier_id"],
                location=row["location"],
                status=row["status"],
                lead_time_days=row["lead_time_days"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            items.append(item)
        
        return items
    
    async def get_inventory_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU."""
        query = "SELECT * FROM inventory_items WHERE sku = :sku"
        row = await self.database.fetch_one(query, {"sku": sku})
        
        if not row:
            return None
        
        return InventoryItem(
            id=row["id"],
            sku=row["sku"],
            name=row["name"],
            category=row["category"],
            current_stock=row["current_stock"],
            min_stock_threshold=row["min_stock_threshold"],
            max_stock_capacity=row["max_stock_capacity"],
            unit_cost=row["unit_cost"],
            supplier_id=row["supplier_id"],
            location=row["location"],
            status=row["status"],
            lead_time_days=row["lead_time_days"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
    
    # Sales Data
    async def save_sales_data(self, sales: List[SalesData]):
        """Save sales data to database."""
        if not sales:
            return
        
        query = """
        INSERT INTO sales_data (id, sku, date, quantity_sold, revenue, channel, customer_segment, created_at)
        VALUES (:id, :sku, :date, :quantity_sold, :revenue, :channel, :customer_segment, :created_at)
        """
        
        values = []
        for sale in sales:
            values.append({
                "id": sale.id if hasattr(sale, 'id') else None,
                "sku": sale.sku,
                "date": sale.date,
                "quantity_sold": sale.quantity_sold,
                "revenue": sale.revenue,
                "channel": sale.channel,
                "customer_segment": sale.customer_segment,
                "created_at": datetime.utcnow()
            })
        
        await self.database.execute_many(query, values)
    
    async def get_sales_data(
        self, 
        sku: Optional[str] = None, 
        days: int = 365
    ) -> List[SalesData]:
        """Get sales data from database."""
        base_query = """
        SELECT * FROM sales_data 
        WHERE date >= :start_date
        """
        params = {"start_date": datetime.utcnow() - timedelta(days=days)}
        
        if sku:
            base_query += " AND sku = :sku"
            params["sku"] = sku
        
        base_query += " ORDER BY date DESC"
        
        rows = await self.database.fetch_all(base_query, params)
        
        sales_data = []
        for row in rows:
            sale = SalesData(
                sku=row["sku"],
                date=row["date"],
                quantity_sold=row["quantity_sold"],
                revenue=row["revenue"],
                channel=row["channel"],
                customer_segment=row["customer_segment"]
            )
            sales_data.append(sale)
        
        return sales_data
    
    # Agent Decisions
    async def save_agent_decision(self, decision: AgentDecision) -> AgentDecisionDB:
        """Save agent decision to database."""
        query = """
        INSERT INTO agent_decisions (id, agent_role, item_sku, action_type, priority, 
                                   confidence_score, reasoning, recommended_quantity, 
                                   estimated_cost, deadline, created_at, updated_at)
        VALUES (:id, :agent_role, :item_sku, :action_type, :priority, :confidence_score, 
                :reasoning, :recommended_quantity, :estimated_cost, :deadline, 
                :created_at, :updated_at)
        """
        
        values = {
            "id": decision.id,
            "agent_role": decision.agent_role.value,
            "item_sku": decision.item_sku,
            "action_type": decision.action_type.value,
            "priority": decision.priority.value,
            "confidence_score": decision.confidence_score,
            "reasoning": decision.reasoning,
            "recommended_quantity": decision.recommended_quantity,
            "estimated_cost": decision.estimated_cost,
            "deadline": decision.deadline,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        }
        
        await self.database.execute(query, values)
        return decision
    
    async def get_agent_decisions(
        self, 
        limit: int = 50,
        agent_role: Optional[str] = None
    ) -> List[AgentDecision]:
        """Get agent decisions from database."""
        base_query = "SELECT * FROM agent_decisions"
        params = {"limit": limit}
        
        if agent_role:
            base_query += " WHERE agent_role = :agent_role"
            params["agent_role"] = agent_role
        
        base_query += " ORDER BY created_at DESC LIMIT :limit"
        
        rows = await self.database.fetch_all(base_query, params)
        
        decisions = []
        for row in rows:
            decision = AgentDecision(
                id=row["id"],
                agent_role=row["agent_role"],
                item_sku=row["item_sku"],
                action_type=row["action_type"],
                priority=row["priority"],
                confidence_score=row["confidence_score"],
                reasoning=row["reasoning"],
                recommended_quantity=row["recommended_quantity"],
                estimated_cost=row["estimated_cost"],
                deadline=row["deadline"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            decisions.append(decision)
        
        return decisions
    
    async def approve_decision(self, decision_id: UUID) -> bool:
        """Approve an agent decision."""
        query = """
        UPDATE agent_decisions 
        SET approved = true, updated_at = :updated_at 
        WHERE id = :decision_id
        """
        
        result = await self.database.execute(
            query, 
            {"decision_id": decision_id, "updated_at": datetime.utcnow()}
        )
        
        return result > 0
    
    # Alerts
    async def save_alert(self, alert: Alert) -> AlertDB:
        """Save alert to database."""
        query = """
        INSERT INTO alerts (id, title, message, priority, item_sku, alert_type, 
                          resolved, created_at, updated_at)
        VALUES (:id, :title, :message, :priority, :item_sku, :alert_type, 
                :resolved, :created_at, :updated_at)
        """
        
        values = {
            "id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "priority": alert.priority.value,
            "item_sku": alert.item_sku,
            "alert_type": alert.alert_type,
            "resolved": alert.resolved,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        }
        
        await self.database.execute(query, values)
        return alert
    
    async def get_alerts(
        self, 
        limit: int = 50,
        resolved: Optional[bool] = None
    ) -> List[Alert]:
        """Get alerts from database."""
        base_query = "SELECT * FROM alerts"
        params = {"limit": limit}
        
        if resolved is not None:
            base_query += " WHERE resolved = :resolved"
            params["resolved"] = resolved
        
        base_query += " ORDER BY created_at DESC LIMIT :limit"
        
        rows = await self.database.fetch_all(base_query, params)
        
        alerts = []
        for row in rows:
            alert = Alert(
                id=row["id"],
                title=row["title"],
                message=row["message"],
                priority=row["priority"],
                item_sku=row["item_sku"],
                alert_type=row["alert_type"],
                resolved=row["resolved"],
                resolved_at=row["resolved_at"],
                resolved_by=row["resolved_by"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            alerts.append(alert)
        
        return alerts
    
    # Analytics
    async def get_inventory_analytics(self) -> Dict[str, Any]:
        """Get inventory analytics from database."""
        queries = {
            "total_items": "SELECT COUNT(*) as count FROM inventory_items",
            "total_value": "SELECT SUM(current_stock * unit_cost) as value FROM inventory_items",
            "low_stock_count": "SELECT COUNT(*) as count FROM inventory_items WHERE current_stock <= min_stock_threshold",
            "out_of_stock_count": "SELECT COUNT(*) as count FROM inventory_items WHERE current_stock = 0",
            "avg_stock_level": "SELECT AVG(current_stock) as avg_stock FROM inventory_items"
        }
        
        analytics = {}
        for key, query in queries.items():
            result = await self.database.fetch_one(query)
            if result:
                analytics[key] = result[0] if len(result) == 1 else dict(result)
        
        return analytics


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions
async def get_db():
    """Dependency to get database session."""
    async with db_manager.database.transaction():
        yield db_manager


async def init_database():
    """Initialize database connection."""
    await db_manager.connect()


async def close_database():
    """Close database connection."""
    await db_manager.disconnect()