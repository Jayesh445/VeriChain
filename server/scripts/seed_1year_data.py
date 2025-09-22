"""
Comprehensive Data Seeding Script for VeriChain
Seeds 1 year of historical inventory, sales, and transaction data for forecasting and analysis.
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
from app.services.database import InventoryService, SalesService
from app.models import ItemCategory
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
            StationeryCategory.PAPER: {
                "exam_prep": 2.5,
                "school_opening": 3.0,
                "admission_season": 1.8,
                "festival_season": 1.2,
                "regular_months": 1.0
            },
            StationeryCategory.WRITING_INSTRUMENTS: {
                "exam_prep": 2.8,
                "school_opening": 2.5,
                "admission_season": 2.0,
                "festival_season": 1.3,
                "regular_months": 1.0
            },
            StationeryCategory.OFFICE_SUPPLIES: {
                "exam_prep": 1.5,
                "school_opening": 1.8,
                "admission_season": 1.4,
                "festival_season": 1.6,
                "regular_months": 1.0
            },
            StationeryCategory.ART_CRAFT: {
                "exam_prep": 1.2,
                "school_opening": 2.2,
                "admission_season": 1.8,
                "festival_season": 2.5,
                "regular_months": 1.0
            },
            StationeryCategory.FILING_ORGANIZATION: {
                "exam_prep": 1.8,
                "school_opening": 2.0,
                "admission_season": 2.5,
                "festival_season": 1.1,
                "regular_months": 1.0
            }
        }
        
        # Base daily sales for different categories
        self.base_daily_sales = {
            StationeryCategory.PAPER: 15,
            StationeryCategory.WRITING_INSTRUMENTS: 25,
            StationeryCategory.OFFICE_SUPPLIES: 12,
            StationeryCategory.ART_CRAFT: 8,
            StationeryCategory.FILING_ORGANIZATION: 6
        }
        
        # Item templates for seeding
        self.item_templates = {
            StationeryCategory.PAPER: [
                {"name": "A4 Paper", "sku": "PP-A4-001", "unit_price": 8.50, "base_stock": 500},
                {"name": "A3 Paper", "sku": "PP-A3-001", "unit_price": 12.00, "base_stock": 200},
                {"name": "Letter Paper", "sku": "PP-LT-001", "unit_price": 9.00, "base_stock": 300},
                {"name": "Legal Paper", "sku": "PP-LG-001", "unit_price": 10.50, "base_stock": 150},
                {"name": "Colored Paper", "sku": "PP-CL-001", "unit_price": 15.00, "base_stock": 100}
            ],
            StationeryCategory.WRITING_INSTRUMENTS: [
                {"name": "Ballpoint Pen Black", "sku": "WI-BP-BK", "unit_price": 1.25, "base_stock": 1000},
                {"name": "Ballpoint Pen Blue", "sku": "WI-BP-BL", "unit_price": 1.25, "base_stock": 800},
                {"name": "Gel Pen", "sku": "WI-GP-001", "unit_price": 2.50, "base_stock": 500},
                {"name": "Marker Set", "sku": "WI-MK-001", "unit_price": 12.00, "base_stock": 200},
                {"name": "Pencils HB", "sku": "WI-PC-HB", "unit_price": 0.75, "base_stock": 1200},
                {"name": "Highlighter", "sku": "WI-HL-001", "unit_price": 3.25, "base_stock": 300}
            ],
            StationeryCategory.OFFICE_SUPPLIES: [
                {"name": "Sticky Notes", "sku": "OS-SN-001", "unit_price": 3.75, "base_stock": 400},
                {"name": "Paper Clips", "sku": "OS-PC-001", "unit_price": 2.00, "base_stock": 300},
                {"name": "Stapler", "sku": "OS-ST-001", "unit_price": 15.00, "base_stock": 50},
                {"name": "Tape Dispenser", "sku": "OS-TD-001", "unit_price": 8.50, "base_stock": 75},
                {"name": "Rubber Bands", "sku": "OS-RB-001", "unit_price": 1.50, "base_stock": 200}
            ],
            StationeryCategory.ART_CRAFT: [
                {"name": "Glue Stick", "sku": "AC-GS-001", "unit_price": 2.25, "base_stock": 150},
                {"name": "Scissors", "sku": "AC-SC-001", "unit_price": 6.50, "base_stock": 100},
                {"name": "Craft Paper", "sku": "AC-CP-001", "unit_price": 5.00, "base_stock": 200},
                {"name": "Watercolors", "sku": "AC-WC-001", "unit_price": 18.00, "base_stock": 50},
                {"name": "Drawing Pencils", "sku": "AC-DP-001", "unit_price": 8.00, "base_stock": 80}
            ],
            StationeryCategory.FILING_ORGANIZATION: [
                {"name": "Manila Folders", "sku": "FO-MF-001", "unit_price": 0.85, "base_stock": 500},
                {"name": "Binders", "sku": "FO-BD-001", "unit_price": 12.00, "base_stock": 100},
                {"name": "File Dividers", "sku": "FO-FD-001", "unit_price": 4.50, "base_stock": 200},
                {"name": "Label Sheets", "sku": "FO-LS-001", "unit_price": 6.25, "base_stock": 150},
                {"name": "Storage Boxes", "sku": "FO-SB-001", "unit_price": 25.00, "base_stock": 30}
            ]
        }

    def get_seasonal_period(self, date: datetime) -> str:
        """Determine seasonal period for given date"""
        month = date.month
        
        for period, months in self.educational_calendar.items():
            if month in months:
                return period
        return "regular_months"

    def get_demand_multiplier(self, category: StationeryCategory, date: datetime) -> float:
        """Get demand multiplier for category on specific date"""
        period = self.get_seasonal_period(date)
        return self.seasonal_multipliers[category][period]

    def add_noise(self, base_value: float, noise_factor: float = 0.2) -> float:
        """Add random noise to a base value"""
        noise = random.uniform(-noise_factor, noise_factor)
        return max(0, base_value * (1 + noise))

    async def seed_inventory_items(self, db: AsyncSession):
        """Seed initial inventory items"""
        print("🏗️  Seeding inventory items...")
        
        for category, items in self.item_templates.items():
            for item_data in items:
                # Check if item already exists
                existing = await InventoryService.get_item_by_sku(db, item_data["sku"])
                if existing:
                    print(f"   ↪️  Item {item_data['sku']} already exists, skipping...")
                    continue
                
                item = StationeryItemCreate(
                    sku=item_data["sku"],
                    name=item_data["name"],
                    description=f"{item_data['name']} - Professional grade stationery item",
                    category=category,
                    current_stock=item_data["base_stock"],
                    reorder_level=max(10, item_data["base_stock"] // 10),
                    max_stock_level=item_data["base_stock"] * 2,
                    unit_price=item_data["unit_price"],
                    unit_cost=item_data["unit_price"] * 0.6,  # 40% markup
                    supplier_id=random.randint(1, 3)  # Assuming we have 3 suppliers
                )
                
                try:
                    created_item = await InventoryService.create_item(db, item)
                    print(f"   ✅ Created item: {item_data['name']} ({item_data['sku']})")
                except Exception as e:
                    print(f"   ❌ Failed to create item {item_data['sku']}: {e}")

    async def seed_historical_sales(self, db: AsyncSession):
        """Seed 1 year of historical sales data"""
        print("📊 Seeding historical sales data...")
        
        # Get all items
        items = await InventoryService.get_all_items(db)
        if not items:
            print("   ⚠️  No items found, please seed inventory first")
            return
        
        # Generate sales for each day in the past year
        current_date = self.start_date
        total_sales_created = 0
        
        while current_date <= self.end_date:
            daily_sales = 0
            
            for item in items:
                # Get base daily sales for this category
                base_sales = self.base_daily_sales.get(item.category, 5)
                
                # Apply seasonal multiplier
                multiplier = self.get_demand_multiplier(item.category, current_date)
                
                # Calculate expected sales with noise
                expected_sales = self.add_noise(base_sales * multiplier, 0.3)
                
                # Convert to integer (number of units sold)
                units_sold = max(0, int(expected_sales))
                
                # Skip if no sales for this day
                if units_sold == 0:
                    continue
                
                # Create sales record
                sale = SalesRecordCreate(
                    item_id=item.id,
                    quantity_sold=units_sold,
                    unit_price=item.unit_price * random.uniform(0.95, 1.05),  # Price variation
                    customer_type=random.choice(["school", "office", "individual", "bulk"]),
                    department=random.choice(["primary", "secondary", "higher_ed", "corporate"]),
                    sale_date=current_date
                )
                
                try:
                    await SalesService.create_sales_record(db, sale)
                    daily_sales += units_sold
                    total_sales_created += 1
                except Exception as e:
                    print(f"   ❌ Failed to create sales record: {e}")
            
            # Progress indicator
            if current_date.day == 1:  # Print progress monthly
                print(f"   📅 Processed {current_date.strftime('%B %Y')} - {daily_sales} sales today")
            
            current_date += timedelta(days=1)
        
        print(f"   ✅ Created {total_sales_created} historical sales records")

    async def generate_analytics_data(self, db: AsyncSession):
        """Generate additional analytics data for forecasting"""
        print("📈 Generating analytics data...")
        
        # This would typically involve:
        # 1. Calculating moving averages
        # 2. Trend analysis
        # 3. Seasonal decomposition
        # 4. Demand forecasting models
        # 5. Inventory optimization metrics
        
        # For now, we'll update current stock levels based on sales history
        items = await InventoryService.get_all_items(db)
        
        for item in items:
            # Calculate total sales for this item
            result = await db.execute(
                text("SELECT SUM(quantity_sold) as total_sold FROM sales_records WHERE item_id = :item_id"),
                {"item_id": item.id}
            )
            total_sold = result.scalar() or 0
            
            # Calculate total purchases (simulated restocking)
            restock_frequency = 30  # Restock every 30 days on average
            days_elapsed = (self.end_date - self.start_date).days
            total_restocks = days_elapsed // restock_frequency
            total_purchased = total_restocks * (item.max_stock_level - item.reorder_level)
            
            # Calculate current stock
            starting_stock = item.max_stock_level  # Assume we started with max stock
            current_stock = max(0, starting_stock + total_purchased - total_sold)
            
            # Update current stock
            await db.execute(
                text("UPDATE stationery_items SET current_stock = :stock WHERE id = :item_id"),
                {"stock": current_stock, "item_id": item.id}
            )
        
        await db.commit()
        print("   ✅ Updated current stock levels based on sales history")

    async def run_comprehensive_seeding(self):
        """Run the complete seeding process"""
        print("🚀 Starting comprehensive data seeding for VeriChain...")
        print(f"📅 Seeding data from {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        # Initialize database
        await init_db()
        
        async with AsyncSessionLocal() as db:
            try:
                # Seed inventory items
                await self.seed_inventory_items(db)
                
                # Seed historical sales
                await self.seed_historical_sales(db)
                
                # Generate analytics data
                await self.generate_analytics_data(db)
                
                print("✅ Comprehensive data seeding completed successfully!")
                print("📊 Your VeriChain system now has:")
                print("   - Complete inventory catalog")
                print("   - 1 year of historical sales data")
                print("   - Seasonal demand patterns")
                print("   - Analytics-ready data for forecasting")
                
            except Exception as e:
                print(f"❌ Seeding failed: {e}")
                await db.rollback()
                raise


async def main():
    """Main function to run the seeding"""
    seeder = VeriChainDataSeeder()
    await seeder.run_comprehensive_seeding()


if __name__ == "__main__":
    asyncio.run(main())