from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.models import (
    StationeryItem, Vendor, VendorItem, SalesRecord, Order, OrderItem, 
    AgentDecision, ItemCategory, OrderStatus, VendorStatus, AgentDecisionType
)
from app.core.logging import logger


class InventoryService:
    """Service for inventory-related database operations"""
    
    @staticmethod
    async def get_all_items(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[StationeryItem]:
        """Get all stationery items"""
        query = select(StationeryItem).where(StationeryItem.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_item_by_id(db: AsyncSession, item_id: int) -> Optional[StationeryItem]:
        """Get item by ID"""
        query = select(StationeryItem).where(StationeryItem.id == item_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_item_by_sku(db: AsyncSession, sku: str) -> Optional[StationeryItem]:
        """Get item by SKU"""
        query = select(StationeryItem).where(StationeryItem.sku == sku)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_low_stock_items(db: AsyncSession) -> List[StationeryItem]:
        """Get items with stock below reorder level"""
        query = select(StationeryItem).where(
            and_(
                StationeryItem.current_stock <= StationeryItem.reorder_level,
                StationeryItem.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_out_of_stock_items(db: AsyncSession) -> List[StationeryItem]:
        """Get items that are out of stock"""
        query = select(StationeryItem).where(
            and_(
                StationeryItem.current_stock <= 0,
                StationeryItem.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_overstock_items(db: AsyncSession, threshold_percentage: float = 150.0) -> List[StationeryItem]:
        """Get items with stock above max level"""
        query = select(StationeryItem).where(
            and_(
                StationeryItem.current_stock > (StationeryItem.max_stock_level * threshold_percentage / 100),
                StationeryItem.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_stock(db: AsyncSession, item_id: int, quantity_change: int) -> Optional[StationeryItem]:
        """Update stock quantity for an item"""
        item = await InventoryService.get_item_by_id(db, item_id)
        if item:
            item.current_stock += quantity_change
            item.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(item)
        return item
    
    @staticmethod
    async def get_inventory_summary(db: AsyncSession) -> Dict[str, Any]:
        """Get inventory summary statistics"""
        total_items_query = select(func.count(StationeryItem.id)).where(StationeryItem.is_active == True)
        low_stock_query = select(func.count(StationeryItem.id)).where(
            and_(
                StationeryItem.current_stock <= StationeryItem.reorder_level,
                StationeryItem.is_active == True
            )
        )
        out_of_stock_query = select(func.count(StationeryItem.id)).where(
            and_(
                StationeryItem.current_stock <= 0,
                StationeryItem.is_active == True
            )
        )
        
        total_items = (await db.execute(total_items_query)).scalar()
        low_stock_count = (await db.execute(low_stock_query)).scalar()
        out_of_stock_count = (await db.execute(out_of_stock_query)).scalar()
        
        return {
            "total_items": total_items,
            "low_stock_items": low_stock_count,
            "out_of_stock_items": out_of_stock_count,
            "healthy_stock_items": total_items - low_stock_count - out_of_stock_count
        }


class SalesService:
    """Service for sales-related database operations"""
    
    @staticmethod
    async def create_sale(db: AsyncSession, sale_data: Dict[str, Any]) -> SalesRecord:
        """Create a new sales record"""
        sale = SalesRecord(**sale_data)
        sale.total_amount = sale.quantity_sold * sale.unit_price
        db.add(sale)
        await db.commit()
        await db.refresh(sale)
        
        # Update inventory
        await InventoryService.update_stock(db, sale.item_id, -sale.quantity_sold)
        
        return sale
    
    @staticmethod
    async def get_sales_by_period(
        db: AsyncSession, 
        start_date: datetime, 
        end_date: datetime,
        item_id: Optional[int] = None
    ) -> List[SalesRecord]:
        """Get sales records for a specific period"""
        query = select(SalesRecord).where(
            and_(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            )
        ).options(selectinload(SalesRecord.item))
        
        if item_id:
            query = query.where(SalesRecord.item_id == item_id)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_sales_trends(db: AsyncSession, days: int = 30) -> List[Dict[str, Any]]:
        """Get sales trends for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = select(
            func.date(SalesRecord.sale_date).label('date'),
            func.sum(SalesRecord.quantity_sold).label('total_quantity'),
            func.sum(SalesRecord.total_amount).label('total_amount'),
            func.count(SalesRecord.id).label('transaction_count')
        ).where(
            and_(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            )
        ).group_by(func.date(SalesRecord.sale_date)).order_by(asc('date'))
        
        result = await db.execute(query)
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def get_top_selling_items(db: AsyncSession, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """Get top selling items for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = select(
            StationeryItem.id,
            StationeryItem.sku,
            StationeryItem.name,
            func.sum(SalesRecord.quantity_sold).label('total_sold'),
            func.sum(SalesRecord.total_amount).label('total_revenue')
        ).join(
            SalesRecord, StationeryItem.id == SalesRecord.item_id
        ).where(
            and_(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            )
        ).group_by(
            StationeryItem.id, StationeryItem.sku, StationeryItem.name
        ).order_by(desc('total_sold')).limit(limit)
        
        result = await db.execute(query)
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def detect_sales_anomalies(db: AsyncSession, item_id: int, threshold: float = 2.0) -> Dict[str, Any]:
        """Detect sales anomalies using statistical analysis"""
        # Get last 30 days of sales data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        query = select(
            func.date(SalesRecord.sale_date).label('date'),
            func.sum(SalesRecord.quantity_sold).label('daily_sales')
        ).where(
            and_(
                SalesRecord.item_id == item_id,
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            )
        ).group_by(func.date(SalesRecord.sale_date))
        
        result = await db.execute(query)
        daily_sales = [row.daily_sales for row in result]
        
        if len(daily_sales) < 7:  # Need at least a week of data
            return {"anomaly_detected": False, "reason": "Insufficient data"}
        
        # Basic statistical anomaly detection
        import numpy as np
        sales_array = np.array(daily_sales)
        mean_sales = np.mean(sales_array)
        std_sales = np.std(sales_array)
        
        # Check if recent sales (last 3 days) are anomalous
        recent_sales = daily_sales[-3:] if len(daily_sales) >= 3 else daily_sales
        anomalies = []
        
        for day_sales in recent_sales:
            z_score = abs((day_sales - mean_sales) / std_sales) if std_sales > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "sales": day_sales,
                    "z_score": z_score,
                    "type": "high" if day_sales > mean_sales else "low"
                })
        
        return {
            "anomaly_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "stats": {
                "mean_sales": mean_sales,
                "std_sales": std_sales,
                "recent_avg": np.mean(recent_sales)
            }
        }


class VendorService:
    """Service for vendor-related database operations"""
    
    @staticmethod
    async def get_all_vendors(db: AsyncSession, active_only: bool = True) -> List[Vendor]:
        """Get all vendors"""
        query = select(Vendor)
        if active_only:
            query = query.where(Vendor.status == VendorStatus.ACTIVE)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_vendor_by_id(db: AsyncSession, vendor_id: int) -> Optional[Vendor]:
        """Get vendor by ID"""
        query = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_vendor_items(db: AsyncSession, vendor_id: int) -> List[VendorItem]:
        """Get all items for a vendor"""
        query = select(VendorItem).where(VendorItem.vendor_id == vendor_id).options(
            selectinload(VendorItem.item)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_vendors_for_item(db: AsyncSession, item_id: int) -> List[VendorItem]:
        """Get all vendors that supply a specific item"""
        query = select(VendorItem).where(VendorItem.item_id == item_id).options(
            selectinload(VendorItem.vendor)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_vendor_performance(db: AsyncSession, vendor_id: int, days: int = 90) -> Dict[str, Any]:
        """Get vendor performance metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get orders for this vendor
        orders_query = select(Order).where(
            and_(
                Order.vendor_id == vendor_id,
                Order.order_date >= start_date
            )
        )
        orders_result = await db.execute(orders_query)
        orders = orders_result.scalars().all()
        
        if not orders:
            return {"no_data": True}
        
        # Calculate metrics
        total_orders = len(orders)
        delivered_orders = [o for o in orders if o.status == OrderStatus.DELIVERED]
        on_time_deliveries = [
            o for o in delivered_orders 
            if o.actual_delivery_date and o.expected_delivery_date and 
            o.actual_delivery_date <= o.expected_delivery_date
        ]
        
        performance = {
            "total_orders": total_orders,
            "delivered_orders": len(delivered_orders),
            "on_time_deliveries": len(on_time_deliveries),
            "delivery_rate": len(delivered_orders) / total_orders if total_orders > 0 else 0,
            "on_time_rate": len(on_time_deliveries) / len(delivered_orders) if delivered_orders else 0,
            "total_value": sum(o.total_amount for o in orders),
            "avg_order_value": sum(o.total_amount for o in orders) / total_orders if total_orders > 0 else 0
        }
        
        return performance


class OrderService:
    """Service for order-related database operations"""
    
    @staticmethod
    async def create_order(db: AsyncSession, order_data: Dict[str, Any]) -> Order:
        """Create a new order"""
        # Generate order number
        order_count_query = select(func.count(Order.id))
        order_count = (await db.execute(order_count_query)).scalar()
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{order_count + 1:04d}"
        
        order = Order(
            order_number=order_number,
            vendor_id=order_data["vendor_id"],
            notes=order_data.get("notes"),
            created_by=order_data.get("created_by", "system")
        )
        
        db.add(order)
        await db.flush()  # Get the order ID
        
        # Add order items
        total_amount = 0
        for item_data in order_data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                item_id=item_data["item_id"],
                quantity_ordered=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["quantity"] * item_data["unit_price"]
            )
            total_amount += order_item.total_price
            db.add(order_item)
        
        order.total_amount = total_amount
        await db.commit()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def get_pending_orders(db: AsyncSession) -> List[Order]:
        """Get all pending orders"""
        query = select(Order).where(Order.status == OrderStatus.PENDING).options(
            selectinload(Order.vendor),
            selectinload(Order.items)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_order_status(db: AsyncSession, order_id: int, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        order = await OrderService.get_order_by_id(db, order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            
            if status == OrderStatus.DELIVERED:
                order.actual_delivery_date = datetime.utcnow()
                # Update inventory for delivered items
                for item in order.items:
                    await InventoryService.update_stock(
                        db, item.item_id, item.quantity_received or item.quantity_ordered
                    )
            
            await db.commit()
            await db.refresh(order)
        
        return order
    
    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        query = select(Order).where(Order.id == order_id).options(
            selectinload(Order.vendor),
            selectinload(Order.items)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_overdue_orders(db: AsyncSession) -> List[Order]:
        """Get overdue orders"""
        current_date = datetime.utcnow()
        query = select(Order).where(
            Order.expected_delivery_date < current_date,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.APPROVED, OrderStatus.SHIPPED])
        ).options(
            selectinload(Order.vendor),
            selectinload(Order.items)
        )
        result = await db.execute(query)
        return result.scalars().all()


class AgentDecisionService:
    """Service for agent decision logging and retrieval"""
    
    @staticmethod
    async def log_decision(
        db: AsyncSession,
        decision_type: AgentDecisionType,
        decision_data: Dict[str, Any],
        reasoning: str,
        confidence_score: float,
        item_id: Optional[int] = None,
        vendor_id: Optional[int] = None
    ) -> AgentDecision:
        """Log an agent decision"""
        import json
        
        decision = AgentDecision(
            decision_type=decision_type.value,
            item_id=item_id,
            vendor_id=vendor_id,
            decision_data=json.dumps(decision_data),
            reasoning=reasoning,
            confidence_score=confidence_score
        )
        
        db.add(decision)
        await db.commit()
        await db.refresh(decision)
        
        logger.info(f"Agent decision logged: {decision_type} - {reasoning}")
        
        return decision
    
    @staticmethod
    async def get_recent_decisions(
        db: AsyncSession,
        decision_type: Optional[AgentDecisionType] = None,
        limit: int = 50
    ) -> List[AgentDecision]:
        """Get recent agent decisions"""
        query = select(AgentDecision).order_by(desc(AgentDecision.created_at)).limit(limit)
        
        if decision_type:
            query = query.where(AgentDecision.decision_type == decision_type.value)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_decision_executed(db: AsyncSession, decision_id: int) -> Optional[AgentDecision]:
        """Mark a decision as executed"""
        query = select(AgentDecision).where(AgentDecision.id == decision_id)
        result = await db.execute(query)
        decision = result.scalar_one_or_none()
        
        if decision:
            decision.is_executed = True
            decision.executed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(decision)
        
        return decision