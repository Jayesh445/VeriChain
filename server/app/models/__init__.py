from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Enums
class ItemCategory(str, Enum):
    WRITING = "writing"
    PAPER = "paper"
    OFFICE_SUPPLIES = "office_supplies"
    FILING = "filing"
    BINDING = "binding"
    DESK_ACCESSORIES = "desk_accessories"


class OrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AgentDecisionType(str, Enum):
    REORDER = "REORDER"
    ALERT = "ALERT"
    VENDOR_RISK = "VENDOR_RISK"
    ANOMALY = "ANOMALY"


class UserRole(str, Enum):
    SCM = "scm"  # Supply Chain Manager
    FINANCE = "finance"  # Finance Officer
    ADMIN = "admin"


# SQLAlchemy Models
class StationeryItem(Base):
    __tablename__ = "stationery_items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    brand = Column(String(100))
    unit = Column(String(20), default="piece")
    unit_cost = Column(Float, nullable=False)
    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, nullable=False)
    max_stock_level = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales = relationship("SalesRecord", back_populates="item")
    vendor_items = relationship("VendorItem", back_populates="item")
    orders = relationship("OrderItem", back_populates="item")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.ACTIVE)
    reliability_score = Column(Float, default=5.0)  # 1-10 scale
    avg_delivery_days = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor_items = relationship("VendorItem", back_populates="vendor")
    orders = relationship("Order", back_populates="vendor")


class VendorItem(Base):
    __tablename__ = "vendor_items"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    item_id = Column(Integer, ForeignKey("stationery_items.id"))
    vendor_sku = Column(String(50))
    unit_price = Column(Float, nullable=False)
    minimum_order_quantity = Column(Integer, default=1)
    lead_time_days = Column(Integer, default=7)
    is_preferred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="vendor_items")
    item = relationship("StationeryItem", back_populates="vendor_items")


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("stationery_items.id"))
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    department = Column(String(100))
    employee_id = Column(String(50))
    sale_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    item = relationship("StationeryItem", back_populates="sales")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, default=0.0)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)
    notes = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("stationery_items.id"))
    quantity_ordered = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    quantity_received = Column(Integer, default=0)

    # Relationships
    order = relationship("Order", back_populates="items")
    item = relationship("StationeryItem", back_populates="orders")


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, index=True)
    decision_type = Column(String(50), nullable=False)  # Using String instead of SQLEnum
    item_id = Column(Integer, ForeignKey("stationery_items.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    decision_data = Column(Text)  # JSON data
    reasoning = Column(Text)
    confidence_score = Column(Float)
    is_executed = Column(Boolean, default=False)
    executed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models (API Schemas)
class StationeryItemBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    category: ItemCategory
    brand: Optional[str] = None
    unit: str = "piece"
    unit_cost: float = Field(..., gt=0)
    reorder_level: int = Field(..., ge=0)
    max_stock_level: int = Field(..., ge=0)


class StationeryItemCreate(StationeryItemBase):
    current_stock: int = Field(0, ge=0)


class StationeryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    unit_cost: Optional[float] = None
    current_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    max_stock_level: Optional[int] = None
    is_active: Optional[bool] = None


class StationeryItemResponse(StationeryItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    current_stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[VendorStatus] = None
    reliability_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    avg_delivery_days: Optional[int] = Field(None, ge=1)


class VendorResponse(VendorBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: VendorStatus
    reliability_score: float
    avg_delivery_days: int
    created_at: datetime
    updated_at: datetime


class SalesRecordBase(BaseModel):
    item_id: int
    quantity_sold: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    department: Optional[str] = None
    employee_id: Optional[str] = None


class SalesRecordCreate(SalesRecordBase):
    pass


class SalesRecordResponse(SalesRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    total_amount: float
    sale_date: datetime
    created_at: datetime


class OrderBase(BaseModel):
    vendor_id: int
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[dict] = Field(..., min_items=1)  # [{"item_id": int, "quantity": int, "unit_price": float}]


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    status: OrderStatus
    total_amount: float
    order_date: datetime
    expected_delivery_date: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime


class AgentDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    decision_type: AgentDecisionType
    item_id: Optional[int]
    vendor_id: Optional[int]
    decision_data: str
    reasoning: str
    confidence_score: Optional[float]
    is_executed: bool
    executed_at: Optional[datetime]
    created_at: datetime


class InventoryAlert(BaseModel):
    item_id: int
    sku: str
    name: str
    current_stock: int
    reorder_level: int
    alert_type: str  # "low_stock", "out_of_stock", "overstock"
    severity: str   # "low", "medium", "high", "critical"


class AgentInsight(BaseModel):
    summary: str
    restock_recommendations: List[dict]
    anomaly_alerts: List[dict]
    vendor_risks: List[dict]
    inventory_alerts: List[InventoryAlert]
    confidence_score: float
    generated_at: datetime
    role_specific_data: dict  # Different data for SCM vs Finance roles


class DashboardData(BaseModel):
    total_items: int
    low_stock_items: int
    out_of_stock_items: int
    pending_orders: int
    total_vendors: int
    recent_sales_trend: List[dict]
    top_selling_items: List[dict]
    vendor_performance: List[dict]
    generated_at: datetime