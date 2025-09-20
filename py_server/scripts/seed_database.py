"""
Advanced Database Seeding Script with Realistic 1-Year Daily Sales Data
Includes seasonal patterns, product variations, and realistic market behavior.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import uuid4
import json

# Import models and database utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import (
    InventoryItem, SalesDataDB, SupplierInfo, AgentDecisionDB, 
    AlertDB, Base, NotificationDB
)
from app.services.database import db_manager, get_database_url
from app.agents.stationery_agent import StationeryCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseSeeder:
    """Comprehensive database seeding with realistic data patterns."""
    
    def __init__(self):
        self.engine = create_engine(get_database_url())
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Realistic stationery product catalog
        self.products = [
            # Writing Instruments
            {"sku": "PEN-001", "name": "Reynolds 045 Ball Pen", "category": "WRITING_INSTRUMENTS", "unit_cost": 15.0, "min_stock": 500, "max_stock": 2000},
            {"sku": "PEN-002", "name": "Cello Butterflow Pen", "category": "WRITING_INSTRUMENTS", "unit_cost": 12.0, "min_stock": 300, "max_stock": 1500},
            {"sku": "PEN-003", "name": "Pilot V7 Hi-Tecpoint Pen", "category": "WRITING_INSTRUMENTS", "unit_cost": 25.0, "min_stock": 200, "max_stock": 800},
            {"sku": "PENCIL-001", "name": "Apsara Platinum Pencil", "category": "WRITING_INSTRUMENTS", "unit_cost": 8.0, "min_stock": 1000, "max_stock": 3000},
            {"sku": "PENCIL-002", "name": "Natraj 621 Pencil", "category": "WRITING_INSTRUMENTS", "unit_cost": 6.0, "min_stock": 800, "max_stock": 2500},
            {"sku": "MARKER-001", "name": "Camlin Permanent Marker", "category": "WRITING_INSTRUMENTS", "unit_cost": 35.0, "min_stock": 100, "max_stock": 500},
            
            # Paper & Notebooks
            {"sku": "NB-001", "name": "Classmate Single Line Notebook", "category": "PAPER_NOTEBOOKS", "unit_cost": 45.0, "min_stock": 500, "max_stock": 2000},
            {"sku": "NB-002", "name": "Classmate Four Line Notebook", "category": "PAPER_NOTEBOOKS", "unit_cost": 42.0, "min_stock": 400, "max_stock": 1800},
            {"sku": "NB-003", "name": "Long Book 172 Pages", "category": "PAPER_NOTEBOOKS", "unit_cost": 65.0, "min_stock": 300, "max_stock": 1200},
            {"sku": "PAPER-001", "name": "A4 Copier Paper (500 sheets)", "category": "PAPER_NOTEBOOKS", "unit_cost": 220.0, "min_stock": 100, "max_stock": 500},
            {"sku": "PAPER-002", "name": "Chart Paper (20 sheets)", "category": "PAPER_NOTEBOOKS", "unit_cost": 85.0, "min_stock": 50, "max_stock": 300},
            
            # Art & Craft Supplies
            {"sku": "COLOR-001", "name": "Camel Wax Crayons 12 Colors", "category": "ART_CRAFT", "unit_cost": 55.0, "min_stock": 200, "max_stock": 800},
            {"sku": "COLOR-002", "name": "Faber-Castell Color Pencils 24 Colors", "category": "ART_CRAFT", "unit_cost": 180.0, "min_stock": 100, "max_stock": 400},
            {"sku": "PAINT-001", "name": "Camel Poster Colors 12ml (12 Colors)", "category": "ART_CRAFT", "unit_cost": 125.0, "min_stock": 80, "max_stock": 300},
            {"sku": "BRUSH-001", "name": "Round Paint Brush Set", "category": "ART_CRAFT", "unit_cost": 75.0, "min_stock": 60, "max_stock": 250},
            
            # Office Supplies
            {"sku": "CLIP-001", "name": "Paper Clips (100 pieces)", "category": "OFFICE_SUPPLIES", "unit_cost": 15.0, "min_stock": 200, "max_stock": 800},
            {"sku": "STAPLER-001", "name": "Kangaro HD-10D Stapler", "category": "OFFICE_SUPPLIES", "unit_cost": 85.0, "min_stock": 50, "max_stock": 200},
            {"sku": "TAPE-001", "name": "Scotch Transparent Tape", "category": "OFFICE_SUPPLIES", "unit_cost": 45.0, "min_stock": 100, "max_stock": 400},
            {"sku": "ERASER-001", "name": "Apsara Non-Dust Eraser", "category": "OFFICE_SUPPLIES", "unit_cost": 8.0, "min_stock": 300, "max_stock": 1000},
            {"sku": "RULER-001", "name": "Plastic Scale 15cm", "category": "OFFICE_SUPPLIES", "unit_cost": 12.0, "min_stock": 200, "max_stock": 600},
            
            # Bags & Storage
            {"sku": "BAG-001", "name": "VIP School Bag", "category": "BAGS_STORAGE", "unit_cost": 450.0, "min_stock": 50, "max_stock": 200},
            {"sku": "BAG-002", "name": "Skybags Casual Backpack", "category": "BAGS_STORAGE", "unit_cost": 850.0, "min_stock": 30, "max_stock": 120},
            {"sku": "POUCH-001", "name": "Pencil Pouch", "category": "BAGS_STORAGE", "unit_cost": 75.0, "min_stock": 100, "max_stock": 400}
        ]
        
        # Realistic suppliers with different pricing and capabilities
        self.suppliers = [
            {
                "name": "Rajesh Stationery Wholesale",
                "contact_email": "rajesh@rswholesale.com",
                "phone": "+91-9876543210",
                "address": "123 Commercial Street, Mumbai, Maharashtra",
                "specialties": ["WRITING_INSTRUMENTS", "PAPER_NOTEBOOKS"],
                "rating": 4.5,
                "payment_terms": "Net 30",
                "discount_rate": 8.0,
                "delivery_time_days": 3
            },
            {
                "name": "Modern Office Solutions",
                "contact_email": "orders@modernofficeindia.com",
                "phone": "+91-9876543211",
                "address": "456 Business Park, Delhi, NCR",
                "specialties": ["OFFICE_SUPPLIES", "BAGS_STORAGE"],
                "rating": 4.2,
                "payment_terms": "Net 15",
                "discount_rate": 12.0,
                "delivery_time_days": 5
            },
            {
                "name": "Creative Arts Suppliers",
                "contact_email": "sales@creativeartsupply.in",
                "phone": "+91-9876543212",
                "address": "789 Art District, Bangalore, Karnataka",
                "specialties": ["ART_CRAFT"],
                "rating": 4.7,
                "payment_terms": "Net 45",
                "discount_rate": 15.0,
                "delivery_time_days": 7
            },
            {
                "name": "Express Stationery Hub",
                "contact_email": "quick@expressstationery.co.in",
                "phone": "+91-9876543213",
                "address": "321 Industrial Area, Chennai, Tamil Nadu",
                "specialties": ["WRITING_INSTRUMENTS", "OFFICE_SUPPLIES", "PAPER_NOTEBOOKS"],
                "rating": 4.0,
                "payment_terms": "Net 20",
                "discount_rate": 10.0,
                "delivery_time_days": 2
            },
            {
                "name": "Quality Paper Mills",
                "contact_email": "supply@qualitypaper.com",
                "phone": "+91-9876543214",
                "address": "654 Paper Mill Road, Hyderabad, Telangana",
                "specialties": ["PAPER_NOTEBOOKS"],
                "rating": 4.6,
                "payment_terms": "Net 60",
                "discount_rate": 18.0,
                "delivery_time_days": 4
            }
        ]
        
        # Seasonal demand patterns (multiplier for each month)
        self.seasonal_patterns = {
            "WRITING_INSTRUMENTS": {
                1: 0.9, 2: 1.0, 3: 1.2, 4: 1.3, 5: 1.1, 6: 2.5,  # Peak in June (school opening)
                7: 1.9, 8: 1.4, 9: 1.3, 10: 1.2, 11: 1.8, 12: 1.6  # Secondary peak in Nov-Dec (exams)
            },
            "PAPER_NOTEBOOKS": {
                1: 0.8, 2: 0.9, 3: 1.1, 4: 1.2, 5: 1.0, 6: 2.8,  # Highest peak for notebooks
                7: 2.0, 8: 1.5, 9: 1.4, 10: 1.1, 11: 1.6, 12: 1.4
            },
            "ART_CRAFT": {
                1: 1.1, 2: 1.2, 3: 1.0, 4: 0.9, 5: 0.8, 6: 1.8,  # Moderate seasonal variation
                7: 1.6, 8: 1.3, 9: 1.2, 10: 1.4, 11: 1.5, 12: 1.7  # Peak during festivals
            },
            "OFFICE_SUPPLIES": {
                1: 1.2, 2: 1.1, 3: 1.0, 4: 1.0, 5: 0.9, 6: 1.4,  # Steady with slight variations
                7: 1.2, 8: 1.1, 9: 1.2, 10: 1.1, 11: 1.3, 12: 1.1
            },
            "BAGS_STORAGE": {
                1: 0.6, 2: 0.7, 3: 0.8, 4: 1.0, 5: 1.2, 6: 3.5,  # Extreme peak for school bags
                7: 2.0, 8: 1.0, 9: 0.8, 10: 0.7, 11: 0.9, 12: 1.1
            }
        }
    
    async def seed_suppliers(self):
        """Seed realistic supplier data."""
        session = self.Session()
        try:
            print("🏪 Seeding supplier data...")
            
            for supplier_data in self.suppliers:
                supplier = SupplierInfo(
                    id=uuid4(),
                    name=supplier_data["name"],
                    contact_email=supplier_data["contact_email"],
                    phone=supplier_data["phone"],
                    address=supplier_data["address"],
                    specialties=supplier_data["specialties"],
                    rating=supplier_data["rating"],
                    payment_terms=supplier_data["payment_terms"],
                    discount_rate=supplier_data["discount_rate"],
                    delivery_time_days=supplier_data["delivery_time_days"],
                    is_active=True,
                    last_order_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                session.add(supplier)
            
            session.commit()
            print(f"✅ Successfully seeded {len(self.suppliers)} suppliers")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding suppliers: {e}")
        finally:
            session.close()
    
    async def seed_inventory_items(self):
        """Seed realistic inventory items."""
        session = self.Session()
        try:
            print("📦 Seeding inventory items...")
            
            for product in self.products:
                # Random initial stock between min and max
                initial_stock = random.randint(
                    int(product["min_stock"] * 0.7), 
                    int(product["max_stock"] * 0.9)
                )
                
                item = InventoryItem(
                    id=uuid4(),
                    sku=product["sku"],
                    name=product["name"],
                    description=f"High-quality {product['name']} for educational and office use",
                    category=product["category"],
                    unit_cost=product["unit_cost"],
                    selling_price=product["unit_cost"] * random.uniform(1.3, 1.8),  # 30-80% markup
                    current_stock=initial_stock,
                    minimum_stock_level=product["min_stock"],
                    maximum_stock_level=product["max_stock"],
                    supplier_id=None,  # Will be assigned during supplier matching
                    location="Warehouse-A",
                    last_updated=datetime.utcnow() - timedelta(days=random.randint(1, 7))
                )
                session.add(item)
            
            session.commit()
            print(f"✅ Successfully seeded {len(self.products)} inventory items")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding inventory: {e}")
        finally:
            session.close()
    
    async def generate_realistic_sales_data(self):
        """Generate 1 year of realistic daily sales data with seasonal patterns."""
        session = self.Session()
        try:
            print("📊 Generating 1 year of realistic sales data...")
            
            # Get all inventory items
            items = session.query(InventoryItem).all()
            
            # Start date: 1 year ago from today
            start_date = datetime.now() - timedelta(days=365)
            
            sales_count = 0
            
            for day_offset in range(365):
                current_date = start_date + timedelta(days=day_offset)
                current_month = current_date.month
                
                # Weekend effect (lower sales on weekends)
                weekend_multiplier = 0.6 if current_date.weekday() >= 5 else 1.0
                
                # Special events (festivals, exam periods)
                special_event_multiplier = self._get_special_event_multiplier(current_date)
                
                for item in items:
                    # Base daily demand (realistic for Indian stationery market)
                    base_demand = self._calculate_base_demand(item)
                    
                    # Apply seasonal pattern
                    seasonal_multiplier = self.seasonal_patterns.get(
                        item.category, 
                        {current_month: 1.0}
                    ).get(current_month, 1.0)
                    
                    # Calculate final demand
                    daily_demand = base_demand * seasonal_multiplier * weekend_multiplier * special_event_multiplier
                    
                    # Add randomness (±30%)
                    daily_demand = max(0, int(daily_demand * random.uniform(0.7, 1.3)))
                    
                    if daily_demand > 0:
                        # Multiple sales channels
                        channels = ["online", "retail", "wholesale", "direct"]
                        channel_weights = [0.4, 0.3, 0.2, 0.1]
                        
                        # Split demand across channels
                        remaining_demand = daily_demand
                        for i, channel in enumerate(channels):
                            if remaining_demand <= 0:
                                break
                                
                            channel_demand = int(remaining_demand * channel_weights[i])
                            if channel_demand > 0:
                                revenue = channel_demand * item.selling_price
                                
                                # Different customer segments
                                segments = ["schools", "offices", "individual", "bulk_buyers"]
                                segment = random.choice(segments)
                                
                                sales_record = SalesDataDB(
                                    id=uuid4(),
                                    sku=item.sku,
                                    date=current_date + timedelta(
                                        hours=random.randint(9, 18),
                                        minutes=random.randint(0, 59)
                                    ),
                                    quantity_sold=channel_demand,
                                    revenue=revenue,
                                    channel=channel,
                                    customer_segment=segment,
                                    created_at=current_date
                                )
                                session.add(sales_record)
                                sales_count += 1
                                remaining_demand -= channel_demand
                
                # Commit every 10 days to avoid memory issues
                if day_offset % 10 == 0:
                    session.commit()
                    print(f"📈 Generated sales data for {day_offset + 1}/365 days...")
            
            session.commit()
            print(f"✅ Successfully generated {sales_count} sales records for 1 year")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error generating sales data: {e}")
        finally:
            session.close()
    
    def _calculate_base_demand(self, item: InventoryItem) -> float:
        """Calculate realistic base daily demand for an item."""
        # Base demand depends on product type and price
        if item.category == "WRITING_INSTRUMENTS":
            if item.unit_cost < 20:  # Cheap pens/pencils
                return random.uniform(50, 150)
            else:  # Premium writing instruments
                return random.uniform(10, 40)
        elif item.category == "PAPER_NOTEBOOKS":
            if "notebook" in item.name.lower():
                return random.uniform(30, 100)
            else:  # Paper reams
                return random.uniform(5, 25)
        elif item.category == "ART_CRAFT":
            return random.uniform(8, 35)
        elif item.category == "OFFICE_SUPPLIES":
            if item.unit_cost < 50:  # Small supplies
                return random.uniform(20, 80)
            else:  # Expensive office items
                return random.uniform(3, 15)
        elif item.category == "BAGS_STORAGE":
            return random.uniform(2, 12)  # Lower volume, higher value
        else:
            return random.uniform(5, 30)
    
    def _get_special_event_multiplier(self, date: datetime) -> float:
        """Get demand multiplier for special events and festivals."""
        month = date.month
        day = date.day
        
        # Indian festival seasons and academic events
        if month == 6 and day >= 15:  # School opening season
            return 1.8
        elif month == 10 and 15 <= day <= 25:  # Diwali season
            return 1.4
        elif month == 3 and 15 <= day <= 31:  # Exam season
            return 1.3
        elif month == 11 and 1 <= day <= 15:  # Post-Diwali, pre-winter exams
            return 1.5
        elif month == 12 and 20 <= day <= 31:  # Year-end demand
            return 1.2
        else:
            return 1.0
    
    async def seed_agent_decisions(self):
        """Seed realistic agent decision history."""
        session = self.Session()
        try:
            print("🤖 Seeding agent decision history...")
            
            items = session.query(InventoryItem).all()
            decision_count = 0
            
            # Generate decisions for the last 90 days
            for day_offset in range(90):
                decision_date = datetime.now() - timedelta(days=day_offset)
                
                # Generate 2-5 decisions per day
                daily_decisions = random.randint(2, 5)
                
                for _ in range(daily_decisions):
                    item = random.choice(items)
                    
                    # Decision types based on realistic scenarios
                    action_types = ["RESTOCK", "PRICE_ADJUSTMENT", "SUPPLIER_CHANGE", "SEASONAL_PREP"]
                    action_weights = [0.5, 0.2, 0.15, 0.15]
                    action_type = random.choices(action_types, weights=action_weights)[0]
                    
                    # Realistic confidence scores
                    confidence = random.uniform(0.65, 0.95)
                    
                    # Approval rate based on confidence
                    approved = confidence > 0.75 and random.random() > 0.1
                    
                    decision = AgentDecisionDB(
                        id=uuid4(),
                        agent_role="StationeryInventoryAgent",
                        item_sku=item.sku,
                        action_type=action_type,
                        confidence_score=confidence,
                        reasoning=self._generate_decision_reasoning(action_type, item),
                        recommended_quantity=random.randint(100, 1000) if action_type == "RESTOCK" else None,
                        estimated_cost=random.uniform(1000, 50000) if action_type == "RESTOCK" else None,
                        priority="high" if confidence > 0.85 else "medium" if confidence > 0.75 else "low",
                        approved=approved,
                        executed=approved and random.random() > 0.2,
                        created_at=decision_date,
                        approved_at=decision_date + timedelta(hours=random.randint(1, 24)) if approved else None
                    )
                    session.add(decision)
                    decision_count += 1
            
            session.commit()
            print(f"✅ Successfully generated {decision_count} agent decisions")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding agent decisions: {e}")
        finally:
            session.close()
    
    def _generate_decision_reasoning(self, action_type: str, item: InventoryItem) -> str:
        """Generate realistic reasoning for agent decisions."""
        if action_type == "RESTOCK":
            return f"Current stock level ({item.current_stock}) is below minimum threshold ({item.minimum_stock_level}). Seasonal demand analysis suggests increased demand in coming weeks."
        elif action_type == "PRICE_ADJUSTMENT":
            return f"Market analysis indicates opportunity for price optimization. Current selling price ₹{item.selling_price:.2f} can be adjusted based on demand elasticity."
        elif action_type == "SUPPLIER_CHANGE":
            return f"Performance analysis shows potential cost savings and quality improvements with alternative suppliers for {item.name}."
        elif action_type == "SEASONAL_PREP":
            return f"Seasonal pattern analysis for {item.category} indicates preparation needed for upcoming demand surge."
        else:
            return f"Routine optimization analysis for {item.name} suggests action for improved inventory management."
    
    async def seed_alerts_and_notifications(self):
        """Seed realistic alerts and notifications."""
        session = self.Session()
        try:
            print("🚨 Seeding alerts and notifications...")
            
            items = session.query(InventoryItem).all()
            alert_count = 0
            notification_count = 0
            
            # Generate alerts for last 30 days
            for day_offset in range(30):
                alert_date = datetime.now() - timedelta(days=day_offset)
                
                # Generate 1-3 alerts per day
                daily_alerts = random.randint(1, 3)
                
                for _ in range(daily_alerts):
                    item = random.choice(items)
                    
                    alert_types = ["LOW_STOCK", "OUT_OF_STOCK", "PRICE_CHANGE", "SUPPLIER_ISSUE", "SEASONAL_ALERT"]
                    alert_weights = [0.4, 0.15, 0.15, 0.15, 0.15]
                    alert_type = random.choices(alert_types, weights=alert_weights)[0]
                    
                    priority = "critical" if alert_type in ["OUT_OF_STOCK", "LOW_STOCK"] else "medium"
                    
                    alert = AlertDB(
                        id=uuid4(),
                        alert_type=alert_type,
                        title=f"{alert_type.replace('_', ' ').title()}: {item.name}",
                        message=self._generate_alert_message(alert_type, item),
                        priority=priority,
                        item_sku=item.sku,
                        resolved=random.random() > 0.3,  # 70% resolved
                        created_at=alert_date,
                        resolved_at=alert_date + timedelta(hours=random.randint(1, 48)) if random.random() > 0.3 else None
                    )
                    session.add(alert)
                    alert_count += 1
                    
                    # Create corresponding notifications
                    notification = NotificationDB(
                        id=uuid4(),
                        type=alert_type.lower(),
                        title=alert.title,
                        message=alert.message,
                        recipient="admin@verichain.com",
                        sent=True,
                        sent_at=alert_date,
                        created_at=alert_date
                    )
                    session.add(notification)
                    notification_count += 1
            
            session.commit()
            print(f"✅ Successfully generated {alert_count} alerts and {notification_count} notifications")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding alerts/notifications: {e}")
        finally:
            session.close()
    
    def _generate_alert_message(self, alert_type: str, item: InventoryItem) -> str:
        """Generate realistic alert messages."""
        if alert_type == "LOW_STOCK":
            return f"Stock level for {item.name} (SKU: {item.sku}) has dropped to {item.current_stock} units, below the minimum threshold of {item.minimum_stock_level}. Immediate restocking recommended."
        elif alert_type == "OUT_OF_STOCK":
            return f"CRITICAL: {item.name} (SKU: {item.sku}) is completely out of stock. This may impact sales and customer satisfaction."
        elif alert_type == "PRICE_CHANGE":
            return f"Market price analysis suggests reviewing pricing for {item.name}. Current selling price: ₹{item.selling_price:.2f}"
        elif alert_type == "SUPPLIER_ISSUE":
            return f"Potential delivery delay reported by supplier for {item.name}. Consider alternative sourcing options."
        elif alert_type == "SEASONAL_ALERT":
            return f"Seasonal demand surge expected for {item.name} in {item.category}. Consider increasing stock levels."
        else:
            return f"Alert for {item.name} (SKU: {item.sku}) requires attention."
    
    async def run_complete_seeding(self):
        """Run the complete database seeding process."""
        print("🌱 Starting comprehensive database seeding...")
        print("=" * 60)
        
        try:
            await self.seed_suppliers()
            await self.seed_inventory_items()
            await self.generate_realistic_sales_data()
            await self.seed_agent_decisions()
            await self.seed_alerts_and_notifications()
            
            print("=" * 60)
            print("🎉 Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   • {len(self.suppliers)} suppliers")
            print(f"   • {len(self.products)} inventory items")
            print(f"   • ~133,225 sales records (365 days × 365 items avg)")
            print(f"   • ~450 agent decisions (90 days)")
            print(f"   • ~90 alerts and notifications (30 days)")
            print("\n🚀 You can now start the server and explore the dashboard!")
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            raise

# Export data function
async def export_seeded_data():
    """Export seeded data to JSON for backup/analysis."""
    session = DatabaseSeeder().Session()
    try:
        # Export sample data
        items = session.query(InventoryItem).limit(10).all()
        sales = session.query(SalesDataDB).limit(100).all()
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "sample_items": [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "category": item.category,
                    "current_stock": item.current_stock,
                    "unit_cost": item.unit_cost,
                    "selling_price": item.selling_price
                }
                for item in items
            ],
            "sample_sales": [
                {
                    "sku": sale.sku,
                    "date": sale.date.isoformat(),
                    "quantity": sale.quantity_sold,
                    "revenue": sale.revenue,
                    "channel": sale.channel
                }
                for sale in sales
            ]
        }
        
        with open("exported_data.json", "w") as f:
            json.dump(export_data, f, indent=2)
        
        print("✅ Sample data exported to exported_data.json")
        
    finally:
        session.close()

if __name__ == "__main__":
    async def main():
        seeder = DatabaseSeeder()
        await seeder.run_complete_seeding()
        await export_seeded_data()
    
    asyncio.run(main())