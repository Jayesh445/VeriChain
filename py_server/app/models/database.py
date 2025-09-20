"""
Database models for VeriChain application using SQLAlchemy.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.models import InventoryStatus, Priority, ActionType, AgentRole

Base = declarative_base()


class InventoryItemDB(Base):
    """Database model for inventory items."""
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock_threshold = Column(Integer, nullable=False, default=0)
    max_stock_capacity = Column(Integer, nullable=False, default=100)
    unit_cost = Column(Float, nullable=False, default=0.0)
    supplier_id = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(SQLEnum(InventoryStatus), default=InventoryStatus.IN_STOCK)
    lead_time_days = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SalesDataDB(Base):
    """Database model for sales data."""
    __tablename__ = "sales_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sku = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    quantity_sold = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0.0)
    channel = Column(String(50), default="online")
    customer_segment = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentDecisionDB(Base):
    """Database model for agent decisions."""
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_role = Column(SQLEnum(AgentRole), nullable=False)
    item_sku = Column(String(100), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    priority = Column(SQLEnum(Priority), nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    recommended_quantity = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    approved = Column(Boolean, default=False)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertDB(Base):
    """Database model for alerts."""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(SQLEnum(Priority), nullable=False)
    item_sku = Column(String(100), nullable=True, index=True)
    alert_type = Column(String(50), default="general")
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)