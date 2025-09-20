"""
Core Pydantic models for VeriChain application.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class InventoryStatus(str, Enum):
    """Inventory status enumeration."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class Priority(str, Enum):
    """Priority levels for actions and alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    """Types of actions the agent can recommend."""
    RESTOCK = "restock"
    HOLD = "hold"
    REDUCE_INVENTORY = "reduce_inventory"
    ALERT = "alert"
    OPTIMIZE_STOCK = "optimize_stock"
    FORECAST_DEMAND = "forecast_demand"


class AgentRole(str, Enum):
    """Different agent roles in the system."""
    SUPPLY_CHAIN_MANAGER = "supply_chain_manager"
    INVENTORY_ANALYST = "inventory_analyst"
    DEMAND_FORECASTER = "demand_forecaster"
    PROCUREMENT_SPECIALIST = "procurement_specialist"


# Base Models
class BaseEntity(BaseModel):
    """Base entity with common fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Inventory Models
class InventoryItem(BaseEntity):
    """Inventory item model."""
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    current_stock: int = Field(..., ge=0, description="Current stock quantity")
    min_stock_threshold: int = Field(..., ge=0, description="Minimum stock threshold")
    max_stock_capacity: int = Field(..., ge=0, description="Maximum stock capacity")
    unit_cost: float = Field(..., ge=0, description="Cost per unit")
    supplier_id: Optional[str] = Field(None, description="Supplier identifier")
    location: Optional[str] = Field(None, description="Storage location")
    status: InventoryStatus = Field(default=InventoryStatus.IN_STOCK)
    lead_time_days: int = Field(default=7, ge=0, description="Lead time in days")


class SalesData(BaseModel):
    """Sales data model."""
    sku: str
    date: datetime
    quantity_sold: int = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    channel: str = Field(default="online")
    customer_segment: Optional[str] = None


class SupplierInfo(BaseEntity):
    """Supplier information model."""
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    reliability_score: float = Field(..., ge=0, le=10)
    average_lead_time: int = Field(..., ge=0)
    min_order_quantity: int = Field(default=1, ge=1)


# Agent Models
class AgentDecision(BaseEntity):
    """Agent decision model."""
    agent_role: AgentRole
    item_sku: str
    action_type: ActionType
    priority: Priority
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: str
    recommended_quantity: Optional[int] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMemory(BaseModel):
    """Agent memory for conversation context."""
    conversation_id: UUID = Field(default_factory=uuid4)
    messages: List[Dict[str, str]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# API Request/Response Models
class AgentRequest(BaseModel):
    """Request model for agent actions."""
    agent_role: AgentRole
    inventory_data: List[InventoryItem]
    sales_data: Optional[List[SalesData]] = None
    supplier_data: Optional[List[SupplierInfo]] = None
    user_query: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[UUID] = None


class AgentResponse(BaseModel):
    """Response model for agent actions."""
    success: bool
    agent_role: AgentRole
    decisions: List[AgentDecision]
    summary: str
    conversation_id: UUID
    processing_time: float
    confidence_score: float = Field(..., ge=0, le=1)
    next_actions: Optional[List[str]] = None


class AgentOverride(BaseModel):
    """Model for user override of agent decisions."""
    decision_id: UUID
    approved: bool
    user_notes: Optional[str] = None
    modified_quantity: Optional[int] = Field(None, ge=0)
    modified_deadline: Optional[datetime] = None


# Alert Models
class Alert(BaseEntity):
    """Alert model for notifications."""
    title: str
    message: str
    priority: Priority
    item_sku: Optional[str] = None
    alert_type: str = Field(default="general")
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


# Analytics Models
class InventoryAnalytics(BaseModel):
    """Inventory analytics model."""
    total_items: int
    low_stock_items: int
    out_of_stock_items: int
    total_value: float
    turnover_rate: float
    forecast_accuracy: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DemandForecast(BaseEntity):
    """Demand forecast model."""
    sku: str
    forecast_period_days: int
    predicted_demand: int = Field(..., ge=0)
    confidence_interval_lower: int = Field(..., ge=0)
    confidence_interval_upper: int = Field(..., ge=0)
    forecast_accuracy: Optional[float] = Field(None, ge=0, le=1)
    factors_considered: List[str] = Field(default_factory=list)


# Configuration Models
class AgentConfig(BaseModel):
    """Agent configuration model."""
    model_name: str = Field(default="gemini-1.5-flash")
    temperature: float = Field(default=0.2, ge=0, le=1)
    max_tokens: int = Field(default=1000, gt=0)
    memory_size: int = Field(default=10, gt=0)
    retry_attempts: int = Field(default=3, gt=0)
    timeout_seconds: int = Field(default=30, gt=0)


# Error Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: bool = True
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)