"""
Notification system for stationery inventory management.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json

from pydantic import BaseModel
from loguru import logger

from app.models import AgentDecision, Priority, InventoryItem, Alert


class NotificationType(str, Enum):
    """Types of notifications in the system."""
    ORDER_ALERT = "order_alert"
    STOCK_WARNING = "stock_warning"
    SEASONAL_REMINDER = "seasonal_reminder"
    NEGOTIATION_OPPORTUNITY = "negotiation_opportunity"
    DELIVERY_UPDATE = "delivery_update"
    PRICE_CHANGE = "price_change"
    PATTERN_INSIGHT = "pattern_insight"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


@dataclass
class NotificationMessage:
    """Notification message structure."""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: Priority
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class NotificationTemplate:
    """Templates for different types of notifications."""
    
    @staticmethod
    def create_order_alert(decision: AgentDecision) -> NotificationMessage:
        """Create order alert notification."""
        priority_emoji = {
            Priority.CRITICAL: "🚨",
            Priority.HIGH: "⚠️",
            Priority.MEDIUM: "📋",
            Priority.LOW: "ℹ️"
        }
        
        emoji = priority_emoji.get(decision.priority, "📋")
        
        if decision.recommended_quantity:
            title = f"{emoji} Auto-Order Recommendation: {decision.item_sku}"
            message = f"Recommended to order {decision.recommended_quantity} units of {decision.item_sku}"
            if decision.estimated_cost:
                message += f" (Est. cost: ${decision.estimated_cost:,.2f})"
        else:
            title = f"{emoji} Inventory Alert: {decision.item_sku}"
            message = f"Action required for {decision.item_sku}: {decision.action_type.value}"
        
        return NotificationMessage(
            id=f"order_{decision.id}",
            type=NotificationType.ORDER_ALERT,
            title=title,
            message=message,
            priority=decision.priority,
            data={
                "decision_id": str(decision.id),
                "item_sku": decision.item_sku,
                "action_type": decision.action_type.value,
                "recommended_quantity": decision.recommended_quantity,
                "estimated_cost": decision.estimated_cost,
                "deadline": decision.deadline.isoformat() if decision.deadline else None,
                "reasoning": decision.reasoning
            },
            channels=[NotificationChannel.DASHBOARD, NotificationChannel.PUSH],
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_stock_warning(item: InventoryItem) -> NotificationMessage:
        """Create low stock warning notification."""
        if item.current_stock == 0:
            title = f"🚨 OUT OF STOCK: {item.name}"
            message = f"{item.name} ({item.sku}) is completely out of stock!"
            priority = Priority.CRITICAL
        elif item.current_stock <= item.min_stock_threshold:
            title = f"⚠️ LOW STOCK: {item.name}"
            message = f"{item.name} ({item.sku}) is below minimum threshold ({item.current_stock}/{item.min_stock_threshold})"
            priority = Priority.HIGH
        else:
            title = f"📋 STOCK UPDATE: {item.name}"
            message = f"{item.name} ({item.sku}) stock level: {item.current_stock}"
            priority = Priority.MEDIUM
        
        return NotificationMessage(
            id=f"stock_{item.sku}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=NotificationType.STOCK_WARNING,
            title=title,
            message=message,
            priority=priority,
            data={
                "item_sku": item.sku,
                "item_name": item.name,
                "current_stock": item.current_stock,
                "min_threshold": item.min_stock_threshold,
                "max_capacity": item.max_stock_capacity,
                "unit_cost": item.unit_cost,
                "category": item.category
            },
            channels=[NotificationChannel.DASHBOARD, NotificationChannel.EMAIL],
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_seasonal_reminder(category: str, event: str, days_ahead: int) -> NotificationMessage:
        """Create seasonal reminder notification."""
        title = f"🗓️ Seasonal Alert: {event} in {days_ahead} days"
        message = f"Prepare {category} inventory for upcoming {event}. Historical data shows increased demand."
        
        return NotificationMessage(
            id=f"seasonal_{event}_{datetime.utcnow().strftime('%Y%m%d')}",
            type=NotificationType.SEASONAL_REMINDER,
            title=title,
            message=message,
            priority=Priority.MEDIUM,
            data={
                "category": category,
                "event": event,
                "days_ahead": days_ahead,
                "suggested_actions": [
                    "Review historical demand patterns",
                    "Check supplier availability",
                    "Consider bulk ordering discounts"
                ]
            },
            channels=[NotificationChannel.DASHBOARD, NotificationChannel.EMAIL],
            created_at=datetime.utcnow(),
            scheduled_for=datetime.utcnow() + timedelta(days=1)  # Send tomorrow
        )
    
    @staticmethod
    def create_negotiation_opportunity(total_value: float, categories: List[str]) -> NotificationMessage:
        """Create supplier negotiation opportunity notification."""
        title = f"💰 Negotiation Opportunity: ${total_value:,.2f} bulk order"
        message = f"Bulk order opportunity across {len(categories)} categories. Potential for volume discounts."
        
        return NotificationMessage(
            id=f"negotiation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=NotificationType.NEGOTIATION_OPPORTUNITY,
            title=title,
            message=message,
            priority=Priority.MEDIUM,
            data={
                "total_value": total_value,
                "categories": categories,
                "potential_discount": f"{min(15, max(5, total_value // 2000))}%",
                "recommended_actions": [
                    "Contact suppliers for quotes",
                    "Negotiate volume discounts",
                    "Consider extended payment terms"
                ]
            },
            channels=[NotificationChannel.DASHBOARD],
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_pattern_insight(insight: str, confidence: float, impact: str) -> NotificationMessage:
        """Create pattern analysis insight notification."""
        title = f"📊 Pattern Insight: {insight[:50]}..."
        message = f"AI detected pattern: {insight}"
        
        return NotificationMessage(
            id=f"insight_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=NotificationType.PATTERN_INSIGHT,
            title=title,
            message=message,
            priority=Priority.LOW,
            data={
                "insight": insight,
                "confidence": confidence,
                "impact": impact,
                "recommendation": "Review pattern and adjust ordering strategy accordingly"
            },
            channels=[NotificationChannel.DASHBOARD],
            created_at=datetime.utcnow()
        )


class NotificationManager:
    """
    Manages notifications for the stationery inventory system.
    """
    
    def __init__(self):
        self.notifications: List[NotificationMessage] = []
        self.subscribers: Dict[NotificationChannel, List[Callable]] = {
            channel: [] for channel in NotificationChannel
        }
        self.max_notifications = 1000  # Keep last 1000 notifications
        logger.info("Initialized Notification Manager")
    
    def subscribe(self, channel: NotificationChannel, callback: Callable):
        """Subscribe to notifications on a specific channel."""
        self.subscribers[channel].append(callback)
        logger.info(f"Added subscriber to {channel.value} channel")
    
    def unsubscribe(self, channel: NotificationChannel, callback: Callable):
        """Unsubscribe from notifications on a specific channel."""
        if callback in self.subscribers[channel]:
            self.subscribers[channel].remove(callback)
            logger.info(f"Removed subscriber from {channel.value} channel")
    
    async def send_notification(self, notification: NotificationMessage):
        """Send notification through appropriate channels."""
        # Add to internal storage
        self.notifications.append(notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        # Send through each requested channel
        for channel in notification.channels:
            for callback in self.subscribers[channel]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(notification)
                    else:
                        callback(notification)
                except Exception as e:
                    logger.error(f"Error sending notification through {channel.value}: {e}")
        
        notification.sent_at = datetime.utcnow()
        logger.info(f"Sent notification: {notification.title}")
    
    def create_from_decision(self, decision: AgentDecision) -> NotificationMessage:
        """Create notification from agent decision."""
        return NotificationTemplate.create_order_alert(decision)
    
    def create_from_inventory_item(self, item: InventoryItem) -> NotificationMessage:
        """Create notification from inventory item status."""
        return NotificationTemplate.create_stock_warning(item)
    
    async def process_decisions(self, decisions: List[AgentDecision]):
        """Process agent decisions and create appropriate notifications."""
        for decision in decisions:
            if decision.priority in [Priority.CRITICAL, Priority.HIGH]:
                notification = self.create_from_decision(decision)
                await self.send_notification(notification)
    
    async def check_inventory_alerts(self, inventory_items: List[InventoryItem]):
        """Check inventory items and create alerts for low stock."""
        for item in inventory_items:
            if item.current_stock <= item.min_stock_threshold:
                notification = self.create_from_inventory_item(item)
                await self.send_notification(notification)
    
    async def send_seasonal_reminders(self):
        """Send seasonal reminders based on educational calendar."""
        current_date = datetime.now()
        current_month = current_date.month
        
        # Define seasonal events
        seasonal_events = [
            (4, "School Preparation Season", "educational_books"),
            (6, "Back-to-School Rush", "all_categories"),
            (11, "Exam Season", "writing_instruments"),
            (1, "New Year Session", "paper_products")
        ]
        
        for event_month, event_name, category in seasonal_events:
            # Calculate days until event
            if event_month >= current_month:
                event_date = current_date.replace(month=event_month, day=1)
            else:
                event_date = current_date.replace(year=current_date.year + 1, month=event_month, day=1)
            
            days_ahead = (event_date - current_date).days
            
            # Send reminder 30 days before
            if 25 <= days_ahead <= 35:
                notification = NotificationTemplate.create_seasonal_reminder(
                    category, event_name, days_ahead
                )
                await self.send_notification(notification)
    
    def get_recent_notifications(
        self, 
        count: int = 50, 
        notification_type: Optional[NotificationType] = None,
        priority: Optional[Priority] = None
    ) -> List[NotificationMessage]:
        """Get recent notifications with optional filtering."""
        filtered_notifications = self.notifications
        
        if notification_type:
            filtered_notifications = [n for n in filtered_notifications if n.type == notification_type]
        
        if priority:
            filtered_notifications = [n for n in filtered_notifications if n.priority == priority]
        
        # Sort by creation time (newest first) and limit
        filtered_notifications.sort(key=lambda n: n.created_at, reverse=True)
        return filtered_notifications[:count]
    
    def get_unread_notifications(self) -> List[NotificationMessage]:
        """Get all unread notifications."""
        return [n for n in self.notifications if n.read_at is None]
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read_at = datetime.utcnow()
                logger.info(f"Marked notification {notification_id} as read")
                break
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get statistics about notifications."""
        total = len(self.notifications)
        unread = len(self.get_unread_notifications())
        
        # Count by type
        type_counts = {}
        for notification in self.notifications:
            type_counts[notification.type.value] = type_counts.get(notification.type.value, 0) + 1
        
        # Count by priority
        priority_counts = {}
        for notification in self.notifications:
            priority_counts[notification.priority.value] = priority_counts.get(notification.priority.value, 0) + 1
        
        return {
            "total_notifications": total,
            "unread_notifications": unread,
            "type_breakdown": type_counts,
            "priority_breakdown": priority_counts,
            "read_percentage": ((total - unread) / total * 100) if total > 0 else 0
        }


# Global notification manager instance
notification_manager = NotificationManager()


# Convenience functions for dashboard integration
async def send_order_alert(decision: AgentDecision):
    """Send order alert notification."""
    notification = NotificationTemplate.create_order_alert(decision)
    await notification_manager.send_notification(notification)


async def send_stock_warning(item: InventoryItem):
    """Send stock warning notification."""
    notification = NotificationTemplate.create_stock_warning(item)
    await notification_manager.send_notification(notification)


async def send_seasonal_reminder(category: str, event: str, days_ahead: int):
    """Send seasonal reminder notification."""
    notification = NotificationTemplate.create_seasonal_reminder(category, event, days_ahead)
    await notification_manager.send_notification(notification)


def get_dashboard_notifications(count: int = 20) -> List[Dict[str, Any]]:
    """Get notifications for dashboard display."""
    notifications = notification_manager.get_recent_notifications(count)
    return [notification.to_dict() for notification in notifications]