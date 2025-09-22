"""
Simple Data Seeding Script for VeriChain
Seeds basic inventory and sales data for testing.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os
from sqlalchemy import text

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal, init_db
from app.models import ItemCategory


class SimpleDataSeeder:
    def __init__(self):
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        
        # Basic item data for seeding
        self.items_data = [
            {"sku": "PP-A4-001", "name": "A4 Paper", "category": ItemCategory.PAPER, "unit_cost": 5.0, "stock": 500, "reorder": 50, "max_stock": 1000},
            {"sku": "PP-A3-001", "name": "A3 Paper", "category": ItemCategory.PAPER, "unit_cost": 8.0, "stock": 200, "reorder": 30, "max_stock": 400},
            {"sku": "WI-BP-001", "name": "Ballpoint Pen Black", "category": ItemCategory.WRITING, "unit_cost": 0.75, "stock": 1000, "reorder": 100, "max_stock": 2000},
            {"sku": "WI-BP-002", "name": "Ballpoint Pen Blue", "category": ItemCategory.WRITING, "unit_cost": 0.75, "stock": 800, "reorder": 100, "max_stock": 1500},
            {"sku": "OS-SN-001", "name": "Sticky Notes", "category": ItemCategory.OFFICE_SUPPLIES, "unit_cost": 2.25, "stock": 300, "reorder": 30, "max_stock": 600},
            {"sku": "OS-ST-001", "name": "Stapler", "category": ItemCategory.OFFICE_SUPPLIES, "unit_cost": 9.0, "stock": 50, "reorder": 10, "max_stock": 100},
            {"sku": "FI-MF-001", "name": "Manila Folders", "category": ItemCategory.FILING, "unit_cost": 0.50, "stock": 500, "reorder": 50, "max_stock": 1000},
            {"sku": "FI-BD-001", "name": "Binders", "category": ItemCategory.FILING, "unit_cost": 8.0, "stock": 100, "reorder": 20, "max_stock": 200},
        ]

    async def seed_basic_items(self, db):
        """Seed basic inventory items"""
        print("🏗️  Seeding basic inventory items...")
        
        for item_data in self.items_data:
            # Check if item exists
            result = await db.execute(
                text("SELECT id FROM stationery_items WHERE sku = :sku"),
                {"sku": item_data["sku"]}
            )
            if result.scalar():
                print(f"   ↪️  Item {item_data['sku']} already exists, skipping...")
                continue
            
            # Insert item
            await db.execute(
                text("""
                    INSERT INTO stationery_items 
                    (sku, name, category, unit_cost, current_stock, reorder_level, max_stock_level, created_at, updated_at)
                    VALUES (:sku, :name, :category, :unit_cost, :current_stock, :reorder_level, :max_stock_level, :created_at, :updated_at)
                """),
                {
                    "sku": item_data["sku"],
                    "name": item_data["name"],
                    "category": item_data["category"].value,
                    "unit_cost": item_data["unit_cost"],
                    "current_stock": item_data["stock"],
                    "reorder_level": item_data["reorder"],
                    "max_stock_level": item_data["max_stock"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print(f"   ✅ Created item: {item_data['name']} ({item_data['sku']})")
        
        await db.commit()

    async def seed_basic_vendors(self, db):
        """Seed basic vendor data"""
        print("🏪 Seeding basic vendors...")
        
        vendors = [
            {"name": "Office Plus Supply Co.", "email": "orders@officeplus.com", "phone": "+1-555-0123"},
            {"name": "Premium Stationery Ltd.", "email": "sales@premiumstation.com", "phone": "+1-555-0456"},
            {"name": "Global Office Solutions", "email": "procurement@globaloffice.com", "phone": "+1-555-0789"}
        ]
        
        for vendor_data in vendors:
            # Check if vendor exists
            result = await db.execute(
                text("SELECT id FROM vendors WHERE name = :name"),
                {"name": vendor_data["name"]}
            )
            if result.scalar():
                continue
            
            await db.execute(
                text("""
                    INSERT INTO vendors (name, email, phone, status, reliability_score, created_at, updated_at)
                    VALUES (:name, :email, :phone, 'active', 8.5, :created_at, :updated_at)
                """),
                {
                    "name": vendor_data["name"],
                    "email": vendor_data["email"],
                    "phone": vendor_data["phone"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print(f"   ✅ Created vendor: {vendor_data['name']}")
        
        await db.commit()

    async def seed_historical_sales(self, db):
        """Seed historical sales data"""
        print("📊 Seeding historical sales data...")
        
        # Get all items
        result = await db.execute(text("SELECT id, name, unit_cost FROM stationery_items"))
        items = result.fetchall()
        
        if not items:
            print("   ⚠️  No items found, please seed inventory first")
            return
        
        departments = ["administration", "accounting", "hr", "operations", "marketing"]
        total_sales = 0
        
        # Generate sales for the past year (sampling every few days to avoid too much data)
        current_date = self.start_date
        while current_date <= self.end_date:
            # Skip some days randomly to create realistic patterns
            if random.random() < 0.3:  # Skip 30% of days
                current_date += timedelta(days=1)
                continue
            
            daily_sales = 0
            for item_id, item_name, unit_cost in items:
                # Random number of sales per item per day (0-10)
                sales_count = random.randint(0, 10)
                
                if sales_count > 0:
                    # Calculate unit price with some variation
                    unit_price = unit_cost * random.uniform(1.5, 2.5)  # 50-150% markup
                    total_amount = sales_count * unit_price
                    
                    await db.execute(
                        text("""
                            INSERT INTO sales_records 
                            (item_id, quantity_sold, unit_price, total_amount, department, sale_date, created_at)
                            VALUES (:item_id, :quantity_sold, :unit_price, :total_amount, :department, :sale_date, :created_at)
                        """),
                        {
                            "item_id": item_id,
                            "quantity_sold": sales_count,
                            "unit_price": unit_price,
                            "total_amount": total_amount,
                            "department": random.choice(departments),
                            "sale_date": current_date,
                            "created_at": current_date
                        }
                    )
                    daily_sales += sales_count
                    total_sales += sales_count
            
            # Print progress every month
            if current_date.day == 1:
                print(f"   📅 Processed {current_date.strftime('%B %Y')} - {daily_sales} sales")
            
            current_date += timedelta(days=random.randint(1, 3))  # Skip 1-3 days
        
        await db.commit()
        print(f"   ✅ Created {total_sales} historical sales records")

    async def seed_basic_agent_decisions(self, db):
        """Seed some basic agent decisions"""
        print("🤖 Seeding basic agent decisions...")
        
        decision_types = ["REORDER", "ALERT", "VENDOR_RISK", "ANOMALY"]
        
        # Create agent decisions table if it doesn't exist
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY,
                item_id INTEGER,
                vendor_id INTEGER,
                decision_type VARCHAR(50),
                reasoning TEXT,
                confidence_score FLOAT,
                is_executed BOOLEAN DEFAULT FALSE,
                execution_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Get some items for decisions
        result = await db.execute(text("SELECT id FROM stationery_items LIMIT 5"))
        item_ids = [row[0] for row in result.fetchall()]
        
        for i in range(20):  # Create 20 sample decisions
            decision_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            await db.execute(
                text("""
                    INSERT INTO agent_decisions 
                    (item_id, decision_type, reasoning, confidence_score, is_executed, created_at)
                    VALUES (:item_id, :decision_type, :reasoning, :confidence_score, :is_executed, :created_at)
                """),
                {
                    "item_id": random.choice(item_ids),
                    "decision_type": random.choice(decision_types),
                    "reasoning": f"AI analysis suggests {random.choice(['reordering', 'monitoring', 'investigating'])} this item.",
                    "confidence_score": random.uniform(0.7, 0.98),
                    "is_executed": random.choice([True, False]),
                    "created_at": decision_date
                }
            )
        
        await db.commit()
        print("   ✅ Created sample agent decisions")

    async def run_seeding(self):
        """Run the complete seeding process"""
        print("🚀 Starting basic data seeding for VeriChain...")
        
        # Initialize database
        await init_db()
        
        async with AsyncSessionLocal() as db:
            try:
                await self.seed_basic_vendors(db)
                await self.seed_basic_items(db)
                await self.seed_historical_sales(db)
                await self.seed_basic_agent_decisions(db)
                
                print("✅ Basic data seeding completed successfully!")
                print("📊 Your VeriChain system now has:")
                print("   - Basic inventory items")
                print("   - Historical sales data")
                print("   - Sample vendor information")
                print("   - Agent decision examples")
                
            except Exception as e:
                print(f"❌ Seeding failed: {e}")
                await db.rollback()
                raise


async def main():
    """Main function to run the seeding"""
    seeder = SimpleDataSeeder()
    await seeder.run_seeding()


if __name__ == "__main__":
    asyncio.run(main())