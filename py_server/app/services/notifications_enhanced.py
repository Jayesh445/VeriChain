"""
Enhanced Notification System for VeriChain with Email Integration
Handles real-time notifications, email alerts, and admin communications.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import json
from uuid import uuid4

# Global notification manager instance
notification_manager = None

class NotificationType(str, Enum):
    """Types of notifications in the system."""
    ORDER_ALERT = "order_alert"
    STOCK_WARNING = "stock_warning"
    SEASONAL_REMINDER = "seasonal_reminder"
    NEGOTIATION_OPPORTUNITY = "negotiation_opportunity"
    DELIVERY_UPDATE = "delivery_update"
    PRICE_CHANGE = "price_change"
    PATTERN_INSIGHT = "pattern_insight"
    LOW_STOCK_ALERT = "low_stock_alert"
    AUTO_ORDER_APPROVAL = "auto_order_approval"
    SUPPLIER_RESPONSE = "supplier_response"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class NotificationMessage:
    """Enhanced notification message structure."""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    recipient: str
    action_required: bool = False
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class EnhancedNotificationManager:
    """Enhanced notification manager with email integration."""
    
    def __init__(self):
        self.notifications: List[NotificationMessage] = []
        
        # Admin contacts
        self.admin_contacts = {
            "inventory_manager": "inventory@verichain.com",
            "procurement_manager": "procurement@verichain.com",
            "admin": "admin@verichain.com",
            "finance_manager": "finance@verichain.com"
        }
        
        # Rate limiting
        self.last_email_sent = {}
        self.rate_limits = {
            NotificationType.LOW_STOCK_ALERT: timedelta(hours=4),
            NotificationType.AUTO_ORDER_APPROVAL: timedelta(hours=1),
            NotificationType.SUPPLIER_RESPONSE: timedelta(minutes=30)
        }
    
    async def send_notification(self, type: str, title: str, message: str, 
                              recipient: str, action_required: bool = False,
                              action_url: str = None, channels: List[str] = None,
                              metadata: Dict[str, Any] = None) -> str:
        """Send a notification through specified channels."""
        
        notification_id = str(uuid4())
        
        # Determine priority
        priority = self._determine_priority(type, title, message)
        
        # Default channels
        if channels is None:
            channels = [NotificationChannel.DASHBOARD.value]
            if priority in [NotificationPriority.CRITICAL, NotificationPriority.HIGH]:
                channels.append(NotificationChannel.EMAIL.value)
        
        # Create notification
        notification = NotificationMessage(
            id=notification_id,
            type=NotificationType(type),
            title=title,
            message=message,
            priority=priority,
            data=metadata or {},
            channels=[NotificationChannel(ch) for ch in channels],
            recipient=recipient,
            action_required=action_required,
            action_url=action_url,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        # Check rate limiting
        if not self._is_rate_limited(notification):
            self.notifications.append(notification)
            await self._dispatch_notification(notification)
        
        return notification_id
    
    def _determine_priority(self, type: str, title: str, message: str) -> NotificationPriority:
        """Automatically determine notification priority."""
        critical_keywords = ["out of stock", "critical", "emergency", "urgent", "failed"]
        high_keywords = ["low stock", "approval required", "warning", "alert"]
        
        combined_text = f"{type.lower()} {title.lower()} {message.lower()}"
        
        if any(keyword in combined_text for keyword in critical_keywords):
            return NotificationPriority.CRITICAL
        elif any(keyword in combined_text for keyword in high_keywords):
            return NotificationPriority.HIGH
        elif "order" in combined_text or "supplier" in combined_text:
            return NotificationPriority.MEDIUM
        else:
            return NotificationPriority.LOW
    
    def _is_rate_limited(self, notification: NotificationMessage) -> bool:
        """Check if notification should be rate limited."""
        notification_type = notification.type
        recipient = notification.recipient
        
        if notification_type not in self.rate_limits:
            return False
        
        key = f"{notification_type.value}_{recipient}"
        rate_limit = self.rate_limits[notification_type]
        
        if key in self.last_email_sent:
            time_since_last = datetime.utcnow() - self.last_email_sent[key]
            if time_since_last < rate_limit:
                return True
        
        self.last_email_sent[key] = datetime.utcnow()
        return False
    
    async def _dispatch_notification(self, notification: NotificationMessage):
        """Dispatch notification through all specified channels."""
        for channel in notification.channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(notification)
                elif channel == NotificationChannel.DASHBOARD:
                    await self._send_dashboard_notification(notification)
            except Exception as e:
                print(f"Failed to send notification via {channel.value}: {e}")
    
    async def _send_email_notification(self, notification: NotificationMessage):
        """Send email notification (mock implementation)."""
        print(f"📧 EMAIL: {notification.title} to {notification.recipient}")
        print(f"   Content: {notification.message}")
        notification.sent_at = datetime.utcnow()
    
    async def _send_dashboard_notification(self, notification: NotificationMessage):
        """Handle dashboard notification."""
        print(f"📱 DASHBOARD: {notification.title}")
    
    async def get_notifications(self, recipient: str = None, 
                              unread_only: bool = False,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for dashboard."""
        filtered_notifications = self.notifications
        
        if recipient:
            filtered_notifications = [n for n in filtered_notifications if n.recipient == recipient]
        
        if unread_only:
            filtered_notifications = [n for n in filtered_notifications if not n.read_at]
        
        # Sort by priority and creation time
        priority_order = {
            NotificationPriority.CRITICAL: 0,
            NotificationPriority.HIGH: 1,
            NotificationPriority.MEDIUM: 2,
            NotificationPriority.LOW: 3,
            NotificationPriority.INFO: 4
        }
        
        filtered_notifications.sort(
            key=lambda n: (priority_order.get(n.priority, 5), n.created_at),
            reverse=True
        )
        
        return [n.to_dict() for n in filtered_notifications[:limit]]
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read_at = datetime.utcnow()
                return True
        return False
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics for dashboard."""
        total = len(self.notifications)
        unread = len([n for n in self.notifications if not n.read_at])
        critical = len([n for n in self.notifications if n.priority == NotificationPriority.CRITICAL])
        action_required = len([n for n in self.notifications if n.action_required and not n.acknowledged_at])
        
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = len([n for n in self.notifications if n.created_at > recent_cutoff])
        
        return {
            "total_notifications": total,
            "unread_count": unread,
            "critical_count": critical,
            "action_required_count": action_required,
            "recent_24h": recent
        }
    
    async def send_low_stock_alert(self, item_name: str, sku: str, current_stock: int,
                                 min_stock: int, days_until_stockout: int):
        """Send low stock alert with auto-order options."""
        await self.send_notification(
            type=NotificationType.LOW_STOCK_ALERT.value,
            title=f"🚨 Low Stock Alert: {item_name}",
            message=f"Stock level critical: {current_stock} units remaining (min: {min_stock})",
            recipient=self.admin_contacts["inventory_manager"],
            action_required=True,
            action_url=f"/dashboard/inventory/{sku}",
            channels=[NotificationChannel.EMAIL.value, NotificationChannel.DASHBOARD.value],
            metadata={
                "item_name": item_name,
                "item_sku": sku,
                "current_stock": current_stock,
                "min_threshold": min_stock,
                "days_until_stockout": days_until_stockout
            }
        )
    
    async def send_auto_order_approval(self, item_name: str, sku: str, quantity: int,
                                     estimated_cost: float, supplier_name: str):
        """Send auto-order approval request."""
        await self.send_notification(
            type=NotificationType.AUTO_ORDER_APPROVAL.value,
            title=f"📋 Auto-Order Approval: {item_name}",
            message=f"Approval required for {quantity} units (₹{estimated_cost:,.2f})",
            recipient=self.admin_contacts["procurement_manager"],
            action_required=True,
            action_url=f"/dashboard/orders/approve/{sku}",
            channels=[NotificationChannel.EMAIL.value, NotificationChannel.DASHBOARD.value],
            metadata={
                "item_name": item_name,
                "item_sku": sku,
                "quantity": quantity,
                "estimated_cost": estimated_cost,
                "supplier_name": supplier_name
            }
        )
    
    async def send_seasonal_reminders(self):
        """Send seasonal preparation reminders."""
        seasonal_events = [
            {"event": "Back to School", "category": "WRITING_INSTRUMENTS", "days_ahead": 14},
            {"event": "Diwali Festival", "category": "ART_CRAFT", "days_ahead": 21},
            {"event": "New Year", "category": "OFFICE_SUPPLIES", "days_ahead": 30}
        ]
        
        for event in seasonal_events:
            await self.send_notification(
                type=NotificationType.SEASONAL_REMINDER.value,
                title=f"🗓️ Seasonal Prep: {event['event']}",
                message=f"Prepare {event['category']} inventory for {event['event']} in {event['days_ahead']} days",
                recipient=self.admin_contacts["inventory_manager"],
                channels=[NotificationChannel.DASHBOARD.value],
                metadata=event
            )


# Initialize global instance
notification_manager = EnhancedNotificationManager()