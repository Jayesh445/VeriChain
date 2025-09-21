import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models import (
    StationeryItem, Vendor, VendorItem, SalesRecord, Order, OrderItem,
    ItemCategory, VendorStatus, OrderStatus
)
from app.core.logging import logger


# Stationery items data
STATIONERY_ITEMS = [
    # Writing instruments
    {"sku": "PEN-001", "name": "Blue Ballpoint Pen", "category": ItemCategory.WRITING, "brand": "Pilot", "unit_cost": 1.50, "reorder_level": 50, "max_stock_level": 200},
    {"sku": "PEN-002", "name": "Black Ballpoint Pen", "category": ItemCategory.WRITING, "brand": "Pilot", "unit_cost": 1.50, "reorder_level": 50, "max_stock_level": 200},
    {"sku": "PEN-003", "name": "Red Ballpoint Pen", "category": ItemCategory.WRITING, "brand": "Pilot", "unit_cost": 1.50, "reorder_level": 30, "max_stock_level": 150},
    {"sku": "PENC-001", "name": "HB Pencil", "category": ItemCategory.WRITING, "brand": "Faber-Castell", "unit_cost": 0.75, "reorder_level": 100, "max_stock_level": 500},
    {"sku": "PENC-002", "name": "2B Pencil", "category": ItemCategory.WRITING, "brand": "Faber-Castell", "unit_cost": 0.75, "reorder_level": 50, "max_stock_level": 300},
    {"sku": "MARK-001", "name": "Permanent Marker Black", "category": ItemCategory.WRITING, "brand": "Sharpie", "unit_cost": 2.25, "reorder_level": 25, "max_stock_level": 100},
    {"sku": "MARK-002", "name": "Whiteboard Marker Blue", "category": ItemCategory.WRITING, "brand": "Expo", "unit_cost": 3.00, "reorder_level": 20, "max_stock_level": 80},
    {"sku": "HIGH-001", "name": "Yellow Highlighter", "category": ItemCategory.WRITING, "brand": "Stabilo", "unit_cost": 1.75, "reorder_level": 30, "max_stock_level": 120},

    # Paper products
    {"sku": "PAP-001", "name": "A4 Copy Paper (500 sheets)", "category": ItemCategory.PAPER, "brand": "HP", "unit_cost": 8.50, "reorder_level": 20, "max_stock_level": 100},
    {"sku": "PAP-002", "name": "Legal Size Paper (500 sheets)", "category": ItemCategory.PAPER, "brand": "HP", "unit_cost": 9.00, "reorder_level": 15, "max_stock_level": 75},
    {"sku": "NOT-001", "name": "Spiral Notebook A5", "category": ItemCategory.PAPER, "brand": "Oxford", "unit_cost": 3.50, "reorder_level": 40, "max_stock_level": 200},
    {"sku": "NOT-002", "name": "Sticky Notes 3x3", "category": ItemCategory.PAPER, "brand": "Post-it", "unit_cost": 4.25, "reorder_level": 25, "max_stock_level": 100},
    {"sku": "ENV-001", "name": "Business Envelopes (100 pack)", "category": ItemCategory.PAPER, "brand": "Generic", "unit_cost": 12.00, "reorder_level": 10, "max_stock_level": 50},

    # Office supplies
    {"sku": "CLIP-001", "name": "Paper Clips (100 pack)", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "Generic", "unit_cost": 2.50, "reorder_level": 20, "max_stock_level": 80},
    {"sku": "STAP-001", "name": "Stapler", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "Swingline", "unit_cost": 15.00, "reorder_level": 5, "max_stock_level": 25},
    {"sku": "STAP-002", "name": "Staples (5000 pack)", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "Swingline", "unit_cost": 8.75, "reorder_level": 15, "max_stock_level": 60},
    {"sku": "TAPE-001", "name": "Scotch Tape", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "3M", "unit_cost": 3.25, "reorder_level": 30, "max_stock_level": 120},
    {"sku": "SCIS-001", "name": "Office Scissors", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "Fiskars", "unit_cost": 8.50, "reorder_level": 10, "max_stock_level": 40},
    {"sku": "GLUE-001", "name": "Glue Stick", "category": ItemCategory.OFFICE_SUPPLIES, "brand": "Elmer's", "unit_cost": 2.75, "reorder_level": 25, "max_stock_level": 100},

    # Filing supplies
    {"sku": "FOLD-001", "name": "Manila File Folders (25 pack)", "category": ItemCategory.FILING, "brand": "Pendaflex", "unit_cost": 18.50, "reorder_level": 8, "max_stock_level": 40},
    {"sku": "BIND-001", "name": "3-Ring Binder 1 inch", "category": ItemCategory.FILING, "brand": "Avery", "unit_cost": 6.75, "reorder_level": 15, "max_stock_level": 60},
    {"sku": "BIND-002", "name": "Sheet Protectors (100 pack)", "category": ItemCategory.FILING, "brand": "Avery", "unit_cost": 12.25, "reorder_level": 12, "max_stock_level": 50},
    {"sku": "LABEL-001", "name": "Address Labels (30 per sheet)", "category": ItemCategory.FILING, "brand": "Avery", "unit_cost": 15.00, "reorder_level": 10, "max_stock_level": 40},

    # Desk accessories
    {"sku": "DESK-001", "name": "Desk Organizer", "category": ItemCategory.DESK_ACCESSORIES, "brand": "Sterilite", "unit_cost": 12.50, "reorder_level": 5, "max_stock_level": 20},
    {"sku": "DESK-002", "name": "Letter Tray", "category": ItemCategory.DESK_ACCESSORIES, "brand": "Rubbermaid", "unit_cost": 8.25, "reorder_level": 8, "max_stock_level": 30},
    {"sku": "CALC-001", "name": "Basic Calculator", "category": ItemCategory.DESK_ACCESSORIES, "brand": "Casio", "unit_cost": 18.75, "reorder_level": 5, "max_stock_level": 25},
    {"sku": "HOLE-001", "name": "3-Hole Punch", "category": ItemCategory.DESK_ACCESSORIES, "brand": "Swingline", "unit_cost": 22.50, "reorder_level": 3, "max_stock_level": 15}
]

# Vendor data
VENDORS = [
    {"name": "OfficeMax Supply Co.", "contact_person": "Sarah Johnson", "email": "sarah@officemax.com", "phone": "555-0101", "reliability_score": 8.5, "avg_delivery_days": 3},
    {"name": "Staples Business Solutions", "contact_person": "Mike Chen", "email": "mike.chen@staples.com", "phone": "555-0102", "reliability_score": 9.2, "avg_delivery_days": 2},
    {"name": "Corporate Supplies Inc.", "contact_person": "Lisa Rodriguez", "email": "lisa@corpsupplies.com", "phone": "555-0103", "reliability_score": 7.8, "avg_delivery_days": 5},
    {"name": "Premier Office Products", "contact_person": "David Kim", "email": "david@premier-office.com", "phone": "555-0104", "reliability_score": 8.9, "avg_delivery_days": 3},
    {"name": "QuickOffice Distributors", "contact_person": "Jennifer Smith", "email": "jen@quickoffice.com", "phone": "555-0105", "reliability_score": 7.2, "avg_delivery_days": 7},
]

# Departments for sales generation
DEPARTMENTS = ["Administration", "HR", "Finance", "IT", "Marketing", "Sales", "Operations", "Legal"]


async def seed_stationery_items(db: AsyncSession):
    """Seed stationery items"""
    logger.info("Seeding stationery items...")
    
    for item_data in STATIONERY_ITEMS:
        # Random initial stock between 50% and 150% of reorder level
        min_stock = int(item_data["reorder_level"] * 0.5)
        max_stock = int(item_data["reorder_level"] * 1.5)
        current_stock = random.randint(min_stock, max_stock)
        
        # Some items intentionally low stock for testing
        if random.random() < 0.15:  # 15% chance of very low stock
            current_stock = random.randint(0, item_data["reorder_level"] // 2)
        
        item = StationeryItem(
            sku=item_data["sku"],
            name=item_data["name"],
            category=item_data["category"],
            brand=item_data["brand"],
            unit_cost=item_data["unit_cost"],
            current_stock=current_stock,
            reorder_level=item_data["reorder_level"],
            max_stock_level=item_data["max_stock_level"]
        )
        
        db.add(item)
    
    await db.commit()
    logger.info(f"Seeded {len(STATIONERY_ITEMS)} stationery items")


async def seed_vendors(db: AsyncSession):
    """Seed vendors"""
    logger.info("Seeding vendors...")
    
    for vendor_data in VENDORS:
        vendor = Vendor(
            name=vendor_data["name"],
            contact_person=vendor_data["contact_person"],
            email=vendor_data["email"],
            phone=vendor_data["phone"],
            reliability_score=vendor_data["reliability_score"],
            avg_delivery_days=vendor_data["avg_delivery_days"],
            status=VendorStatus.ACTIVE
        )
        
        db.add(vendor)
    
    await db.commit()
    logger.info(f"Seeded {len(VENDORS)} vendors")


async def seed_vendor_items(db: AsyncSession):
    """Create vendor-item relationships"""
    logger.info("Creating vendor-item relationships...")
    
    # Get all items and vendors
    from sqlalchemy import select
    
    items_result = await db.execute(select(StationeryItem))
    items = items_result.scalars().all()
    
    vendors_result = await db.execute(select(Vendor))
    vendors = vendors_result.scalars().all()
    
    vendor_items_created = 0
    
    for item in items:
        # Each item is available from 2-4 vendors
        num_vendors = random.randint(2, min(4, len(vendors)))
        selected_vendors = random.sample(vendors, num_vendors)
        
        for i, vendor in enumerate(selected_vendors):
            # Price variation: primary vendor has base cost, others have slight markup
            price_multiplier = 1.0 if i == 0 else random.uniform(1.05, 1.25)
            unit_price = round(item.unit_cost * price_multiplier, 2)
            
            # Lead time varies by vendor
            lead_time = vendor.avg_delivery_days + random.randint(-1, 2)
            lead_time = max(1, lead_time)
            
            vendor_item = VendorItem(
                vendor_id=vendor.id,
                item_id=item.id,
                vendor_sku=f"{vendor.name[:3].upper()}-{item.sku}",
                unit_price=unit_price,
                minimum_order_quantity=random.choice([1, 5, 10, 25]),
                lead_time_days=lead_time,
                is_preferred=(i == 0)  # First vendor is preferred
            )
            
            db.add(vendor_item)
            vendor_items_created += 1
    
    await db.commit()
    logger.info(f"Created {vendor_items_created} vendor-item relationships")


async def seed_sales_records(db: AsyncSession):
    """Generate realistic sales records for the last 60 days"""
    logger.info("Generating sales records...")
    
    from sqlalchemy import select
    
    # Get all items
    items_result = await db.execute(select(StationeryItem))
    items = items_result.scalars().all()
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=60)
    
    sales_created = 0
    
    # Generate sales for each day
    current_date = start_date
    while current_date <= end_date:
        # Random number of sales per day (0-15)
        daily_sales = random.randint(0, 15)
        
        # Weekend sales are typically lower
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            daily_sales = int(daily_sales * 0.3)
        
        for _ in range(daily_sales):
            # Select random item with weighted probability
            # More common items (lower reorder levels usually mean higher usage)
            item = random.choice(items)
            
            # Quantity sold - most sales are small quantities
            if random.random() < 0.7:  # 70% are small quantities
                quantity = random.randint(1, 5)
            elif random.random() < 0.9:  # 20% are medium quantities
                quantity = random.randint(6, 15)
            else:  # 10% are large quantities
                quantity = random.randint(16, 30)
            
            # Price with some variation (±10%)
            price_variation = random.uniform(0.9, 1.1)
            unit_price = round(item.unit_cost * price_variation * 1.5, 2)  # 50% markup typical
            
            # Random time during the day
            sale_time = current_date.replace(
                hour=random.randint(8, 17),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            sale = SalesRecord(
                item_id=item.id,
                quantity_sold=quantity,
                unit_price=unit_price,
                total_amount=quantity * unit_price,
                department=random.choice(DEPARTMENTS),
                employee_id=f"EMP{random.randint(1000, 9999)}",
                sale_date=sale_time
            )
            
            db.add(sale)
            sales_created += 1
        
        current_date += timedelta(days=1)
    
    await db.commit()
    
    # Update inventory based on sales
    await update_inventory_from_sales(db, items)
    
    logger.info(f"Generated {sales_created} sales records")


async def update_inventory_from_sales(db: AsyncSession, items):
    """Update inventory levels based on generated sales"""
    logger.info("Updating inventory levels based on sales...")
    
    from sqlalchemy import select, func
    
    for item in items:
        # Calculate total sales for this item
        sales_query = select(func.sum(SalesRecord.quantity_sold)).where(
            SalesRecord.item_id == item.id
        )
        result = await db.execute(sales_query)
        total_sold = result.scalar() or 0
        
        # Reduce current stock
        item.current_stock = max(0, item.current_stock - total_sold)
    
    await db.commit()
    logger.info("Inventory levels updated")


async def seed_sample_orders(db: AsyncSession):
    """Create some sample orders"""
    logger.info("Creating sample orders...")
    
    from sqlalchemy import select
    
    vendors_result = await db.execute(select(Vendor))
    vendors = vendors_result.scalars().all()
    
    items_result = await db.execute(select(StationeryItem))
    items = items_result.scalars().all()
    
    # Create 5-10 sample orders
    num_orders = random.randint(5, 10)
    
    for i in range(num_orders):
        vendor = random.choice(vendors)
        
        # Order date in the last 30 days
        order_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        # Generate order number
        order_number = f"ORD-{order_date.strftime('%Y%m%d')}-{i+1:04d}"
        
        # Random status
        if random.random() < 0.3:
            status = OrderStatus.DELIVERED
            actual_delivery = order_date + timedelta(days=vendor.avg_delivery_days + random.randint(-1, 2))
        elif random.random() < 0.6:
            status = OrderStatus.SHIPPED
            actual_delivery = None
        else:
            status = OrderStatus.PENDING
            actual_delivery = None
        
        expected_delivery = order_date + timedelta(days=vendor.avg_delivery_days)
        
        order = Order(
            order_number=order_number,
            vendor_id=vendor.id,
            status=status,
            order_date=order_date,
            expected_delivery_date=expected_delivery,
            actual_delivery_date=actual_delivery,
            notes=f"Sample order from {vendor.name}",
            created_by="system_seed"
        )
        
        db.add(order)
        await db.flush()  # Get the order ID
        
        # Add 1-5 items to each order
        num_items = random.randint(1, 5)
        selected_items = random.sample(items, num_items)
        
        total_amount = 0
        
        for item in selected_items:
            # Get vendor price for this item
            vendor_item_query = select(VendorItem).where(
                VendorItem.vendor_id == vendor.id,
                VendorItem.item_id == item.id
            )
            vendor_item_result = await db.execute(vendor_item_query)
            vendor_item = vendor_item_result.scalar_one_or_none()
            
            if vendor_item:
                quantity = random.randint(10, 100)
                unit_price = vendor_item.unit_price
                total_price = quantity * unit_price
                
                order_item = OrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity_ordered=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    quantity_received=quantity if status == OrderStatus.DELIVERED else 0
                )
                
                db.add(order_item)
                total_amount += total_price
        
        order.total_amount = total_amount
    
    await db.commit()
    logger.info(f"Created {num_orders} sample orders")


async def main():
    """Main seeding function"""
    logger.info("Starting database seeding...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as db:
        try:
            # Seed in order
            await seed_stationery_items(db)
            await seed_vendors(db)
            await seed_vendor_items(db)
            await seed_sales_records(db)
            await seed_sample_orders(db)
            
            logger.info("Database seeding completed successfully!")
            
            # Print summary
            from sqlalchemy import select, func
            
            item_count = await db.execute(select(func.count(StationeryItem.id)))
            vendor_count = await db.execute(select(func.count(Vendor.id)))
            sales_count = await db.execute(select(func.count(SalesRecord.id)))
            order_count = await db.execute(select(func.count(Order.id)))
            
            print("\n" + "="*50)
            print("DATABASE SEEDING SUMMARY")
            print("="*50)
            print(f"Stationery Items: {item_count.scalar()}")
            print(f"Vendors: {vendor_count.scalar()}")
            print(f"Sales Records: {sales_count.scalar()}")
            print(f"Orders: {order_count.scalar()}")
            print("="*50)
            
        except Exception as e:
            logger.error(f"Error during seeding: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())