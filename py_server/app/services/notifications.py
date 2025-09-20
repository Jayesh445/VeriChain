"""
Advanced Notification System for VeriChain with Email Integration and Smart Alerts
Handles real-time notifications, email alerts, and admin communications.
"""

import asyncio
import smtplib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import json
import random
from uuid import uuid4

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
    LOW_STOCK_ALERT = "low_stock_alert"
    AUTO_ORDER_APPROVAL = "auto_order_approval"
    SUPPLIER_RESPONSE = "supplier_response"
    SYSTEM_ALERT = "system_alert"
    NEGOTIATION_SUCCESS = "negotiation_success"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    WHATSAPP = "whatsapp"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    CRITICAL = "critical"    # Immediate attention required
    HIGH = "high"           # Important but not urgent
    MEDIUM = "medium"       # Standard notifications
    LOW = "low"            # Informational
    INFO = "info"          # System messages


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
    
    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def get_age_minutes(self) -> int:
        """Get notification age in minutes."""
        return int((datetime.utcnow() - self.created_at).total_seconds() / 60)


class EmailTemplates:
    """Professional email templates for different notification types."""
    
    @staticmethod
    def low_stock_alert(item_name: str, sku: str, current_stock: int, 
                       min_stock: int, days_until_stockout: int) -> Dict[str, str]:
        """Professional low stock alert email."""
        
        urgency = "CRITICAL" if current_stock == 0 else "HIGH" if days_until_stockout <= 3 else "MEDIUM"
        
        subject = f"🚨 {urgency} STOCK ALERT: {item_name} - Action Required"
        
        html_body = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .alert-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .action-button {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .urgent {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 VeriChain Stock Alert</h1>
                </div>
                
                <div class="content">
                    <h2>Immediate Action Required: Low Stock Alert</h2>
                    
                    <div class="alert-box">
                        <h3>📦 Product Details:</h3>
                        <ul>
                            <li><strong>Product:</strong> {item_name}</li>
                            <li><strong>SKU:</strong> {sku}</li>
                            <li><strong>Current Stock:</strong> <span class="urgent">{current_stock} units</span></li>
                            <li><strong>Minimum Required:</strong> {min_stock} units</li>
                            <li><strong>Days Until Stockout:</strong> <span class="urgent">{days_until_stockout} days</span></li>
                        </ul>
                    </div>
                    
                    <h3>🎯 Recommended Actions:</h3>
                    <ol>
                        <li>Review auto-ordering recommendations in the dashboard</li>
                        <li>Contact suppliers for immediate availability</li>
                        <li>Consider expedited shipping if necessary</li>
                        <li>Notify sales team of potential stock limitations</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:3000/dashboard/inventory/{sku}" class="action-button">
                            View in Dashboard →
                        </a>
                        <a href="http://localhost:3000/dashboard/orders/approve" class="action-button" style="background: #28a745;">
                            Approve Auto Orders →
                        </a>
                    </div>
                    
                    <p><em>This alert was generated by VeriChain AI monitoring system at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</em></p>
                </div>
                
                <div class="footer">
                    <p>VeriChain Inventory Management System | 
                    <a href="mailto:support@verichain.com" style="color: #ccc;">support@verichain.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        VeriChain Stock Alert - Action Required
        
        URGENT: Low Stock Alert for {item_name}
        
        Product Details:
        - Product: {item_name}
        - SKU: {sku}
        - Current Stock: {current_stock} units
        - Minimum Required: {min_stock} units
        - Days Until Stockout: {days_until_stockout} days
        
        Recommended Actions:
        1. Review auto-ordering recommendations
        2. Contact suppliers for immediate availability
        3. Consider expedited shipping if necessary
        4. Notify sales team of limitations
        
        Dashboard: http://localhost:3000/dashboard/inventory/{sku}
        Approve Orders: http://localhost:3000/dashboard/orders/approve
        
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {
            "subject": subject,
            "html": html_body,
            "text": text_body
        }
    
    @staticmethod
    def auto_order_approval(item_name: str, sku: str, quantity: int, 
                          estimated_cost: float, supplier_name: str) -> Dict[str, str]:
        """Auto-order approval request email."""
        
        subject = f"📋 Auto-Order Approval Required: {item_name} - ₹{estimated_cost:,.2f}"
        
        html_body = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .order-box {{ background: white; border: 1px solid #dee2e6; padding: 20px; margin: 15px 0; border-radius: 5px; }}
                .approve-btn {{ background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
                .reject-btn {{ background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .highlight {{ color: #007bff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 VeriChain Auto-Order System</h1>
                </div>
                
                <div class="content">
                    <h2>Purchase Order Approval Required</h2>
                    <p>Our AI system has identified a restocking need and prepared an auto-order for your approval.</p>
                    
                    <div class="order-box">
                        <h3>📦 Order Details:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Product:</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{item_name}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>SKU:</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{sku}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Quantity:</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;"><span class="highlight">{quantity} units</span></td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Supplier:</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{supplier_name}</td></tr>
                            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Estimated Cost:</strong></td><td style="padding: 8px; border-bottom: 1px solid #eee;"><span class="highlight">₹{estimated_cost:,.2f}</span></td></tr>
                        </table>
                    </div>
                    
                    <h3>🎯 AI Reasoning:</h3>
                    <p>Based on current stock levels, seasonal demand patterns, and historical sales data, this order is recommended to prevent stockouts and maintain optimal inventory levels.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:3000/dashboard/orders/approve/{sku}?action=approve" class="approve-btn">
                            ✅ Approve Order
                        </a>
                        <a href="http://localhost:3000/dashboard/orders/approve/{sku}?action=reject" class="reject-btn">
                            ❌ Reject Order
                        </a>
                    </div>
                    
                    <p style="font-size: 12px; color: #666;">
                        <em>Note: This order requires approval due to the amount or urgency level. 
                        You can modify auto-approval settings in the dashboard.</em>
                    </p>
                </div>
                
                <div class="footer">
                    <p>VeriChain AI Inventory Management | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "subject": subject,
            "html": html_body,
            "text": f"Auto-Order Approval Required: {item_name} - {quantity} units - ₹{estimated_cost:,.2f}"
        }
    
    @staticmethod
    def supplier_negotiation_complete(item_name: str, supplier_name: str, 
                                    original_price: float, final_price: float,
                                    savings: float) -> Dict[str, str]:
        """Supplier negotiation completion email."""
        
        savings_percentage = (savings / original_price) * 100
        subject = f"💰 Negotiation Success: {savings_percentage:.1f}% savings on {item_name}"
        
        html_body = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8f9fa; }}
                .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; margin: 15px 0; border-radius: 5px; }}
                .savings {{ font-size: 24px; color: #28a745; font-weight: bold; }}
                .footer {{ background: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Negotiation Successful!</h1>
                </div>
                
                <div class="content">
                    <h2>AI Negotiation Completed Successfully</h2>
                    
                    <div class="success-box">
                        <h3>💰 Savings Achieved:</h3>
                        <p class="savings">₹{savings:,.2f} saved ({savings_percentage:.1f}%)</p>
                        
                        <table style="width: 100%; margin-top: 20px;">
                            <tr><td><strong>Product:</strong></td><td>{item_name}</td></tr>
                            <tr><td><strong>Supplier:</strong></td><td>{supplier_name}</td></tr>
                            <tr><td><strong>Original Price:</strong></td><td>₹{original_price:.2f}</td></tr>
                            <tr><td><strong>Final Price:</strong></td><td>₹{final_price:.2f}</td></tr>
                        </table>
                    </div>
                    
                    <p>Our AI negotiation agent successfully secured better pricing through strategic negotiation. 
                    The order is now ready for processing with the approved terms.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:3000/dashboard/negotiations" 
                           style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                            View Negotiation Details →
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>VeriChain AI Procurement | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return {
            "subject": subject,
            "html": html_body,
            "text": f"Negotiation successful: ₹{savings:,.2f} saved on {item_name}"
        }


class EnhancedNotificationManager:
    """Enhanced notification manager with email integration and smart features."""
    
    def __init__(self):
        self.notifications: List[NotificationMessage] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Email configuration
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "alerts@verichain.com",
            "password": "your_app_password",  # Use environment variable in production
            "sender_name": "VeriChain Alert System"
        }
        
        # Admin contacts
        self.admin_contacts = {
            "inventory_manager": "inventory@verichain.com",
            "procurement_manager": "procurement@verichain.com",
            "admin": "admin@verichain.com",
            "finance_manager": "finance@verichain.com"
        }
        
        # Notification batching and rate limiting
        self.email_batch: List[NotificationMessage] = []
        self.last_email_sent = {}
        self.rate_limits = {
            NotificationType.LOW_STOCK_ALERT: timedelta(hours=4),  # Max once per 4 hours per item
            NotificationType.AUTO_ORDER_APPROVAL: timedelta(hours=1),  # Max once per hour per item
            NotificationType.SUPPLIER_RESPONSE: timedelta(minutes=30)  # Max once per 30 min
        }
    
    async def send_notification(self, type: str, title: str, message: str, 
                              recipient: str, action_required: bool = False,
                              action_url: str = None, channels: List[str] = None,
                              metadata: Dict[str, Any] = None) -> str:
        """Send a notification through specified channels."""
        
        notification_id = str(uuid4())
        
        # Determine priority based on type and content
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
            expires_at=datetime.utcnow() + timedelta(days=7)  # Default 7-day expiry
        )
        
        # Check rate limiting
        if self._is_rate_limited(notification):
            logger.info(f"Notification rate limited: {type} for {recipient}")
            return notification_id
        
        # Add to notifications list
        self.notifications.append(notification)
        
        # Send through channels
        await self._dispatch_notification(notification)
        
        logger.info(f"Notification sent: {title} to {recipient}")
        return notification_id
    
    def _determine_priority(self, type: str, title: str, message: str) -> NotificationPriority:
        """Automatically determine notification priority."""
        
        # Critical keywords
        critical_keywords = ["out of stock", "critical", "emergency", "urgent", "failed"]
        high_keywords = ["low stock", "approval required", "warning", "alert"]
        
        type_lower = type.lower()
        title_lower = title.lower()
        message_lower = message.lower()
        
        combined_text = f"{type_lower} {title_lower} {message_lower}"
        
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
                elif channel == NotificationChannel.PUSH:
                    await self._send_push_notification(notification)
                # Add other channels as needed
                
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
    
    async def _send_email_notification(self, notification: NotificationMessage):
        """Send email notification with professional templates."""
        
        try:
            # Generate email content based on notification type
            email_content = await self._generate_email_content(notification)
            
            # Send email (mock implementation for demo)
            await self._send_email(
                to_email=notification.recipient,
                subject=email_content["subject"],
                html_body=email_content.get("html", ""),
                text_body=email_content.get("text", notification.message)
            )
            
            notification.sent_at = datetime.utcnow()
            logger.info(f"Email sent to {notification.recipient}: {notification.title}")
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
    
    async def _generate_email_content(self, notification: NotificationMessage) -> Dict[str, str]:
        """Generate appropriate email content based on notification type."""
        
        if notification.type == NotificationType.LOW_STOCK_ALERT:
            data = notification.data
            return EmailTemplates.low_stock_alert(
                item_name=data.get("item_name", "Unknown Item"),
                sku=data.get("item_sku", ""),
                current_stock=data.get("current_stock", 0),
                min_stock=data.get("min_threshold", 0),
                days_until_stockout=data.get("days_until_stockout", 0)
            )
        
        elif notification.type == NotificationType.AUTO_ORDER_APPROVAL:
            data = notification.data
            return EmailTemplates.auto_order_approval(
                item_name=data.get("item_name", "Unknown Item"),
                sku=data.get("item_sku", ""),
                quantity=data.get("quantity", 0),
                estimated_cost=data.get("estimated_cost", 0),
                supplier_name=data.get("supplier_name", "Unknown Supplier")
            )
        
        elif notification.type == NotificationType.SUPPLIER_RESPONSE:
            data = notification.data
            return EmailTemplates.supplier_negotiation_complete(
                item_name=data.get("item_name", "Unknown Item"),
                supplier_name=data.get("supplier_name", "Unknown Supplier"),
                original_price=data.get("original_price", 0),
                final_price=data.get("final_price", 0),
                savings=data.get("savings", 0)
            )
        
        else:
            # Default email template
            return {
                "subject": notification.title,
                "text": notification.message,
                "html": f"<html><body><h2>{notification.title}</h2><p>{notification.message}</p></body></html>"
            }
    
    async def _send_email(self, to_email: str, subject: str, 
                         html_body: str = "", text_body: str = ""):
        """Send actual email (mock implementation for demo)."""
        
        print(f"📧 EMAIL SENT TO: {to_email}")
        print(f"📋 SUBJECT: {subject}")
        print(f"📄 PREVIEW: {text_body[:100]}...")
        
        # In production, use actual SMTP:
        # try:
        #     msg = MimeMultipart('alternative')
        #     msg['Subject'] = subject
        #     msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['email']}>"
        #     msg['To'] = to_email
        #     
        #     if text_body:
        #         msg.attach(MimeText(text_body, 'plain'))
        #     if html_body:
        #         msg.attach(MimeText(html_body, 'html'))
        #     
        #     server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        #     server.starttls()
        #     server.login(self.email_config['email'], self.email_config['password'])
        #     server.send_message(msg)
        #     server.quit()
        # except Exception as e:
        #     logger.error(f"SMTP error: {e}")
    
    async def _send_dashboard_notification(self, notification: NotificationMessage):
        """Handle dashboard notification (stored in memory for demo)."""
        # In production, this would push to websocket connections or store in database
        logger.info(f"Dashboard notification: {notification.title}")
    
    async def _send_push_notification(self, notification: NotificationMessage):
        """Handle push notification (mock implementation)."""
        print(f"📱 PUSH: {notification.title} - {notification.message[:50]}...")
    
    # API Methods for Dashboard Integration
    
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
    
    async def acknowledge_notification(self, notification_id: str) -> bool:
        """Acknowledge action-required notification."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.acknowledged_at = datetime.utcnow()
                return True
        return False
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics for dashboard."""
        
        total = len(self.notifications)
        unread = len([n for n in self.notifications if not n.read_at])
        critical = len([n for n in self.notifications if n.priority == NotificationPriority.CRITICAL])
        action_required = len([n for n in self.notifications if n.action_required and not n.acknowledged_at])
        
        # Recent notifications (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = len([n for n in self.notifications if n.created_at > recent_cutoff])
        
        return {
            "total_notifications": total,
            "unread_count": unread,
            "critical_count": critical,
            "action_required_count": action_required,
            "recent_24h": recent,
            "email_sent_today": len([n for n in self.notifications 
                                   if n.sent_at and n.sent_at.date() == datetime.now().date()]),
            "avg_response_time_minutes": 15  # Mock data
        }
    
    # Utility methods for auto-ordering integration
    
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
                "days_until_stockout": days_until_stockout,
                "urgency_level": "critical" if current_stock == 0 else "high"
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
                "supplier_name": supplier_name,
                "approval_deadline": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
        )
    
    async def send_seasonal_reminders(self):
        """Send seasonal preparation reminders."""
        # Mock seasonal events
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


# Global notification manager instance
notification_manager = EnhancedNotificationManager()
    
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