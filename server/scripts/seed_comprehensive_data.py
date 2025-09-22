"""
Comprehensive Data Seeding Script for VeriChain
Seeds 1 year of historical inventory, sales, and transaction data for forecasting and analysis.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_async_session, init_db
from app.services.database import InventoryService, SalesService
from app.models import StationeryCategory
from sqlalchemy.ext.asyncio import AsyncSession

class VeriChainDataSeeder:
    def __init__(self):
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        
        # Educational calendar periods (months where demand spikes)
        self.educational_calendar = {
            "exam_prep": [3, 11, 12],  # March, November, December
            "school_opening": [6, 7],   # June, July
            "admission_season": [4, 5], # April, May
            "festival_season": [9, 10], # September, October
            "regular_months": [1, 2, 8] # January, February, August
        }
        
        # Seasonal multipliers for different categories
        self.seasonal_multipliers = {
            "paper": {
                "exam_prep": 2.5,
                "school_opening": 3.0,
                "admission_season": 1.8,
                "festival_season": 1.2,
                "regular_months": 1.0
            },
            "writing": {
                "exam_prep": 2.8,
                "school_opening": 2.5,
                "admission_season": 2.0,
                "festival_season": 1.3,
                "regular_months": 1.0
            },
            "office": {
                "exam_prep": 1.5,
                "school_opening": 1.8,
                "admission_season": 1.4,
                "festival_season": 1.6,
                "regular_months": 1.0
            },
            "filing": {
                "exam_prep": 1.3,
                "school_opening": 2.0,
                "admission_season": 1.7,
                "festival_season": 1.1,
                "regular_months": 1.0
            },
            "art": {
                "exam_prep": 1.2,
                "school_opening": 2.2,
                "admission_season": 1.9,
                "festival_season": 2.0,
                "regular_months": 1.0
            }
        }

    async def seed_suppliers(self):
        """Seed supplier data."""
        suppliers = [
            {
                "name": "Office Plus Supply Co.",
                "contact_email": "orders@officeplus.com",
                "contact_phone": "+1-555-0123",
                "address": "123 Business Ave, Commerce City, CA 90210",
                "status": "active",
                "rating": 4.5,
                "payment_terms": "Net 30",
                "delivery_time_days": 3,
                "minimum_order_value": 500.00
            },
            {
                "name": "Premium Stationery Ltd.",
                "contact_email": "sales@premiumstation.com",
                "contact_phone": "+1-555-0456",
                "address": "456 Supply Street, Trade Town, NY 10001",
                "status": "active",
                "rating": 4.2,
                "payment_terms": "Net 15",
                "delivery_time_days": 5,
                "minimum_order_value": 750.00
            },
            {
                "name": "Educational Supplies Corp",
                "contact_email": "info@edusupplies.com",
                "contact_phone": "+1-555-0789",
                "address": "789 Education Blvd, Scholar City, TX 75001",
                "status": "active",
                "rating": 4.7,
                "payment_terms": "Net 45",
                "delivery_time_days": 2,
                "minimum_order_value": 300.00
            },
            {
                "name": "Bulk Paper Solutions",
                "contact_email": "orders@bulkpaper.com",
                "contact_phone": "+1-555-0321",
                "address": "321 Paper Mill Rd, Industry Park, IL 60601",
                "status": "active",
                "rating": 4.0,
                "payment_terms": "Net 60",
                "delivery_time_days": 7,
                "minimum_order_value": 1000.00
            }
        ]
        
        print("🏢 Seeding suppliers...")
        for supplier_data in suppliers:
            await db_manager.create_supplier(supplier_data)
        print(f"✅ Created {len(suppliers)} suppliers")

    async def seed_inventory_items(self):
        """Seed comprehensive inventory items."""
        items = [
            # Paper products
            {
                "sku": "PP-A4-001",
                "name": "A4 Paper - Premium White",
                "description": "High-quality A4 printing paper (500 sheets per ream)",
                "category": "paper",
                "current_stock": 150,
                "reorder_level": 50,
                "max_stock": 500,
                "unit_price": 8.50,
                "unit": "ream",
                "supplier_id": 1,
                "shelf_life_days": None,
                "weight_kg": 2.5
            },
            {
                "sku": "PP-A4-002",
                "name": "A4 Paper - Economy",
                "description": "Cost-effective A4 printing paper (500 sheets per ream)",
                "category": "paper",
                "current_stock": 200,
                "reorder_level": 75,
                "max_stock": 600,
                "unit_price": 6.75,
                "unit": "ream",
                "supplier_id": 4,
                "shelf_life_days": None,
                "weight_kg": 2.3
            },
            {
                "sku": "PP-A3-001",
                "name": "A3 Paper - Premium",
                "description": "Large format A3 paper for presentations",
                "category": "paper",
                "current_stock": 50,
                "reorder_level": 20,
                "max_stock": 150,
                "unit_price": 15.25,
                "unit": "ream",
                "supplier_id": 1,
                "shelf_life_days": None,
                "weight_kg": 4.0
            },
            
            # Writing instruments
            {
                "sku": "PEN-BP-001",
                "name": "Ballpoint Pens - Black",
                "description": "Professional black ballpoint pens (pack of 10)",
                "category": "writing",
                "current_stock": 25,
                "reorder_level": 30,
                "max_stock": 200,
                "unit_price": 12.50,
                "unit": "pack",
                "supplier_id": 2,
                "shelf_life_days": 1095,  # 3 years
                "weight_kg": 0.1
            },
            {
                "sku": "PEN-BP-002",
                "name": "Ballpoint Pens - Blue",
                "description": "Professional blue ballpoint pens (pack of 10)",
                "category": "writing",
                "current_stock": 30,
                "reorder_level": 25,
                "max_stock": 180,
                "unit_price": 12.50,
                "unit": "pack",
                "supplier_id": 2,
                "shelf_life_days": 1095,
                "weight_kg": 0.1
            },
            {
                "sku": "PEN-GP-001",
                "name": "Gel Pens - Assorted Colors",
                "description": "Smooth gel pens in assorted colors (pack of 12)",
                "category": "writing",
                "current_stock": 40,
                "reorder_level": 20,
                "max_stock": 120,
                "unit_price": 18.75,
                "unit": "pack",
                "supplier_id": 3,
                "shelf_life_days": 730,  # 2 years
                "weight_kg": 0.15
            },
            {
                "sku": "PEN-MRK-001",
                "name": "Permanent Markers - Black",
                "description": "Heavy duty permanent markers (pack of 6)",
                "category": "writing",
                "current_stock": 35,
                "reorder_level": 15,
                "max_stock": 100,
                "unit_price": 22.50,
                "unit": "pack",
                "supplier_id": 2,
                "shelf_life_days": 1460,  # 4 years
                "weight_kg": 0.2
            },
            
            # Office supplies
            {
                "sku": "STN-SN-001",
                "name": "Sticky Notes - Yellow 3x3",
                "description": "Classic yellow sticky notes 3x3 inch (pack of 12 pads)",
                "category": "office",
                "current_stock": 80,
                "reorder_level": 20,
                "max_stock": 150,
                "unit_price": 18.75,
                "unit": "pack",
                "supplier_id": 1,
                "shelf_life_days": 1825,  # 5 years
                "weight_kg": 0.3
            },
            {
                "sku": "STN-SN-002",
                "name": "Sticky Notes - Assorted Colors",
                "description": "Multi-color sticky notes 3x3 inch (pack of 12 pads)",
                "category": "office",
                "current_stock": 60,
                "reorder_level": 15,
                "max_stock": 120,
                "unit_price": 22.50,
                "unit": "pack",
                "supplier_id": 1,
                "shelf_life_days": 1825,
                "weight_kg": 0.3
            },
            {
                "sku": "STN-TAP-001",
                "name": "Scotch Tape - Clear",
                "description": "Clear adhesive tape 1 inch width (pack of 6 rolls)",
                "category": "office",
                "current_stock": 40,
                "reorder_level": 15,
                "max_stock": 75,
                "unit_price": 15.00,
                "unit": "pack",
                "supplier_id": 2,
                "shelf_life_days": None,
                "weight_kg": 0.4
            },
            {
                "sku": "STN-STP-001",
                "name": "Stapler - Heavy Duty",
                "description": "Professional heavy duty stapler with staples",
                "category": "office",
                "current_stock": 15,
                "reorder_level": 5,
                "max_stock": 40,
                "unit_price": 45.00,
                "unit": "piece",
                "supplier_id": 3,
                "shelf_life_days": None,
                "weight_kg": 0.8
            },
            
            # Filing supplies
            {
                "sku": "FLD-PP-001",
                "name": "Manila Folders - Letter Size",
                "description": "Standard manila file folders letter size (pack of 100)",
                "category": "filing",
                "current_stock": 5,
                "reorder_level": 10,
                "max_stock": 100,
                "unit_price": 25.50,
                "unit": "pack",
                "supplier_id": 1,
                "shelf_life_days": None,
                "weight_kg": 2.0
            },
            {
                "sku": "FLD-HF-001",
                "name": "Hanging Folders - Letter Size",
                "description": "Hanging file folders with tabs (pack of 25)",
                "category": "filing",
                "current_stock": 20,
                "reorder_level": 8,
                "max_stock": 60,
                "unit_price": 32.75,
                "unit": "pack",
                "supplier_id": 1,
                "shelf_life_days": None,
                "weight_kg": 1.5
            },
            
            # Art supplies
            {
                "sku": "ART-CLR-001",
                "name": "Colored Pencils - 24 Set",
                "description": "Professional colored pencils set of 24 colors",
                "category": "art",
                "current_stock": 30,
                "reorder_level": 12,
                "max_stock": 80,
                "unit_price": 35.00,
                "unit": "set",
                "supplier_id": 3,
                "shelf_life_days": None,
                "weight_kg": 0.5
            },
            {
                "sku": "ART-MRK-001",
                "name": "Art Markers - 48 Set",
                "description": "Professional art markers with fine and broad tips",
                "category": "art",
                "current_stock": 20,
                "reorder_level": 8,
                "max_stock": 50,
                "unit_price": 85.00,
                "unit": "set",
                "supplier_id": 3,
                "shelf_life_days": 1095,
                "weight_kg": 1.2
            }
        ]
        
        print("📦 Seeding inventory items...")
        for item_data in items:
            await db_manager.create_inventory_item(item_data)
        print(f"✅ Created {len(items)} inventory items")

    def get_seasonal_period(self, date: datetime) -> str:
        """Get the seasonal period for a given date."""
        month = date.month
        for period, months in self.educational_calendar.items():
            if month in months:
                return period
        return "regular_months"

    def get_demand_multiplier(self, category: str, date: datetime) -> float:
        """Get demand multiplier for a category and date."""
        period = self.get_seasonal_period(date)
        return self.seasonal_multipliers.get(category, {}).get(period, 1.0)

    async def seed_historical_sales(self):
        """Seed 1 year of historical sales data with seasonal patterns."""
        print("📊 Seeding historical sales data...")
        
        # Get all inventory items
        items = await db_manager.get_inventory_items()
        
        sales_data = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Simulate daily sales for each item
            for item in items:
                category = item.get("category", "office")
                base_daily_usage = self.get_base_daily_usage(category, item.get("unit_price", 10))
                
                # Apply seasonal multiplier
                multiplier = self.get_demand_multiplier(category, current_date)
                daily_usage = int(base_daily_usage * multiplier)
                
                # Add some randomness (±30%)
                daily_usage = max(0, daily_usage + random.randint(-int(daily_usage * 0.3), int(daily_usage * 0.3)))
                
                if daily_usage > 0:
                    # Create sales record
                    sale = {
                        "item_id": item["id"],
                        "quantity_sold": daily_usage,
                        "unit_price": item.get("unit_price", 10),
                        "total_amount": daily_usage * item.get("unit_price", 10),
                        "customer_type": random.choice(["education", "office", "individual"]),
                        "department": random.choice(["administration", "academics", "maintenance", "library"]),
                        "sale_date": current_date.isoformat()
                    }
                    sales_data.append(sale)
            
            current_date += timedelta(days=1)
        
        # Batch insert sales data
        print(f"💾 Inserting {len(sales_data)} sales records...")
        for sale in sales_data:
            await db_manager.create_sales_record(sale)
        
        print(f"✅ Created {len(sales_data)} sales records")

    def get_base_daily_usage(self, category: str, unit_price: float) -> int:
        """Get base daily usage for an item based on category and price."""
        # Higher priced items typically have lower daily usage
        price_factor = max(0.1, 10 / unit_price)
        
        base_usage = {
            "paper": 5,      # 5 reams per day base
            "writing": 3,    # 3 packs per day base
            "office": 2,     # 2 units per day base
            "filing": 1,     # 1 pack per day base
            "art": 1         # 1 set per day base
        }
        
        return int(base_usage.get(category, 2) * price_factor)

    async def seed_historical_transactions(self):
        """Seed historical purchase transactions and stock movements."""
        print("💰 Seeding historical transactions...")
        
        items = await db_manager.get_inventory_items()
        transactions = []
        
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Simulate weekly restocking
            if current_date.weekday() == 0:  # Monday restocking
                for item in items:
                    # Simulate restocking based on usage patterns
                    if random.random() < 0.3:  # 30% chance of restocking each week
                        reorder_quantity = random.randint(
                            item.get("reorder_level", 20),
                            item.get("max_stock", 100) - item.get("current_stock", 50)
                        )
                        
                        if reorder_quantity > 0:
                            transaction = {
                                "type": "purchase",
                                "item_id": item["id"],
                                "quantity": reorder_quantity,
                                "unit_price": item.get("unit_price", 10),
                                "total_amount": reorder_quantity * item.get("unit_price", 10),
                                "supplier_id": item.get("supplier_id", 1),
                                "transaction_date": current_date.isoformat(),
                                "notes": f"Weekly restock - {item['name']}",
                                "status": "completed"
                            }
                            transactions.append(transaction)
            
            current_date += timedelta(days=1)
        
        # Insert transactions
        print(f"💾 Inserting {len(transactions)} transaction records...")
        for transaction in transactions:
            await db_manager.create_transaction(transaction)
        
        print(f"✅ Created {len(transactions)} transaction records")

    async def seed_agent_decisions(self):
        """Seed historical AI agent decisions."""
        print("🤖 Seeding AI agent decisions...")
        
        items = await db_manager.get_inventory_items()
        decisions = []
        
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Simulate agent decisions every 3 days
            if (current_date - self.start_date).days % 3 == 0:
                # Random agent decision
                item = random.choice(items)
                decision_types = ["reorder", "alert", "optimization", "analysis"]
                decision_type = random.choice(decision_types)
                
                decision = {
                    "decision_type": decision_type,
                    "item_id": item["id"],
                    "reasoning": self.generate_decision_reasoning(decision_type, item),
                    "confidence_score": random.uniform(0.7, 0.98),
                    "is_executed": random.choice([True, False]),
                    "created_at": current_date.isoformat(),
                    "execution_result": "Executed successfully" if random.choice([True, False]) else None
                }
                decisions.append(decision)
            
            current_date += timedelta(days=1)
        
        # Insert decisions
        print(f"💾 Inserting {len(decisions)} agent decisions...")
        for decision in decisions:
            await db_manager.create_agent_decision(decision)
        
        print(f"✅ Created {len(decisions)} agent decisions")

    def generate_decision_reasoning(self, decision_type: str, item: Dict) -> str:
        """Generate realistic reasoning for agent decisions."""
        reasonings = {
            "reorder": [
                f"{item['name']} below minimum stock threshold. Auto-reorder triggered.",
                f"Predicted stockout for {item['name']} in 5 days based on usage patterns.",
                f"Seasonal demand spike detected for {item['name']}. Proactive restocking recommended."
            ],
            "alert": [
                f"High usage pattern detected for {item['name']}. Consider increasing stock levels.",
                f"Supplier delivery delay reported for {item['name']}. Monitor stock closely.",
                f"Price increase alert for {item['name']}. Consider bulk ordering before price change."
            ],
            "optimization": [
                f"{item['name']} showing seasonal demand pattern. Adjusting reorder points.",
                f"Storage optimization: {item['name']} taking excessive warehouse space.",
                f"Cost optimization opportunity: bulk discount available for {item['name']}."
            ],
            "analysis": [
                f"Weekly analysis complete for {item['name']}. Performance within normal parameters.",
                f"Demand forecasting updated for {item['name']} based on recent trends.",
                f"Supplier performance analysis for {item['name']} shows consistent delivery."
            ]
        }
        
        return random.choice(reasonings.get(decision_type, ["Routine analysis performed."]))

    async def update_current_stock_levels(self):
        """Update current stock levels based on historical data."""
        print("📊 Updating current stock levels based on historical data...")
        
        items = await db_manager.get_inventory_items()
        
        for item in items:
            # Calculate net stock change from sales and purchases
            sales_total = await db_manager.get_total_sales_for_item(item["id"])
            purchases_total = await db_manager.get_total_purchases_for_item(item["id"])
            
            # Calculate current stock
            starting_stock = item.get("max_stock", 100) // 2  # Start at 50% capacity
            current_stock = starting_stock + (purchases_total or 0) - (sales_total or 0)
            current_stock = max(0, current_stock)  # Ensure non-negative
            
            # Update item stock
            await db_manager.update_item_current_stock(item["id"], current_stock)
        
        print("✅ Updated current stock levels")

    async def run_complete_seed(self):
        """Run the complete seeding process."""
        print("🌱 Starting VeriChain comprehensive data seeding...")
        print(f"📅 Seeding data from {self.start_date.date()} to {self.end_date.date()}")
        
        try:
            # Initialize database
            await db_manager.init_database()
            
            # Seed data in order
            await self.seed_suppliers()
            await self.seed_inventory_items()
            await self.seed_historical_sales()
            await self.seed_historical_transactions()
            await self.seed_agent_decisions()
            await self.update_current_stock_levels()
            
            print("🎉 VeriChain data seeding completed successfully!")
            print("\n📈 Seeded data summary:")
            print("   • 4 suppliers with different terms and ratings")
            print("   • 15 diverse inventory items across 5 categories")
            print("   • 365 days of historical sales data with seasonal patterns")
            print("   • Weekly purchase transactions and stock movements")
            print("   • AI agent decisions and recommendations")
            print("   • Realistic current stock levels")
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            raise


async def main():
    """Main seeding function."""
    seeder = VeriChainDataSeeder()
    await seeder.run_complete_seed()


if __name__ == "__main__":
    asyncio.run(main())