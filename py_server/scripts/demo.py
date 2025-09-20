#!/usr/bin/env python3
"""
VeriChain System Demo Script
Demonstrates the complete AI-powered stationery inventory management system.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.agents.stationery_agent import StationeryInventoryAgent
    from app.models import *
    from app.services.database import db_manager
    from app.services.notifications import notification_manager
    from app.utils.logging import setup_logging
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Dependencies not available: {e}")

def create_sample_inventory():
    """Create comprehensive sample inventory data."""
    items = [
        # Books and Educational Materials
        InventoryItem(
            id="BOOK_001",
            name="Mathematics Textbook Grade 10",
            category=StationeryCategory.BOOKS,
            current_stock=25,
            min_stock_level=50,
            max_stock_level=200,
            unit_price=45.99,
            supplier="Educational Publishers Ltd",
            last_order_date=datetime.now() - timedelta(days=30),
            seasonal_demand_pattern={
                "jan": 0.2, "feb": 0.3, "mar": 0.4, "apr": 0.5,
                "may": 0.6, "jun": 0.8, "jul": 1.2, "aug": 2.0,  # Back to school peak
                "sep": 1.5, "oct": 0.8, "nov": 0.6, "dec": 0.7
            }
        ),
        InventoryItem(
            id="BOOK_002", 
            name="English Literature Anthology",
            category=StationeryCategory.BOOKS,
            current_stock=15,
            min_stock_level=40,
            max_stock_level=150,
            unit_price=32.50,
            supplier="Literary Works Inc",
            seasonal_demand_pattern={
                "jan": 0.3, "feb": 0.4, "mar": 0.5, "apr": 0.6,
                "may": 0.8, "jun": 0.9, "jul": 1.5, "aug": 2.2,
                "sep": 1.8, "oct": 1.0, "nov": 0.7, "dec": 0.8
            }
        ),
        
        # Writing Instruments
        InventoryItem(
            id="PEN_001",
            name="Blue Ballpoint Pens (Pack of 10)",
            category=StationeryCategory.PENS,
            current_stock=80,
            min_stock_level=100,
            max_stock_level=500,
            unit_price=12.99,
            supplier="Writing Solutions Co",
            seasonal_demand_pattern={
                "jan": 0.8, "feb": 0.9, "mar": 1.0, "apr": 1.2,
                "may": 1.8, "jun": 1.0, "jul": 1.4, "aug": 2.5,  # High demand
                "sep": 2.0, "oct": 1.3, "nov": 1.5, "dec": 2.2   # Exam season
            }
        ),
        InventoryItem(
            id="PEN_002",
            name="Mechanical Pencils 0.5mm",
            category=StationeryCategory.PENS,
            current_stock=45,
            min_stock_level=60,
            max_stock_level=300,
            unit_price=8.75,
            supplier="Precision Writing Ltd",
            seasonal_demand_pattern={
                "jan": 0.7, "feb": 0.8, "mar": 1.1, "apr": 1.3,
                "may": 1.9, "jun": 1.2, "jul": 1.6, "aug": 2.8,
                "sep": 2.2, "oct": 1.5, "nov": 1.8, "dec": 2.5
            }
        ),
        
        # Notebooks and Paper
        InventoryItem(
            id="NOTE_001",
            name="A4 Ruled Notebooks (200 pages)",
            category=StationeryCategory.NOTEBOOKS,
            current_stock=30,
            min_stock_level=75,
            max_stock_level=400,
            unit_price=15.50,
            supplier="Paper Products Inc",
            seasonal_demand_pattern={
                "jan": 0.4, "feb": 0.5, "mar": 0.7, "apr": 0.8,
                "may": 0.6, "jun": 0.5, "jul": 1.8, "aug": 3.0,  # Peak demand
                "sep": 2.5, "oct": 1.2, "nov": 1.0, "dec": 1.1
            }
        ),
        InventoryItem(
            id="NOTE_002",
            name="Graph Paper Notebooks",
            category=StationeryCategory.NOTEBOOKS,
            current_stock=20,
            min_stock_level=50,
            max_stock_level=200,
            unit_price=18.25,
            supplier="Specialty Papers Ltd",
            seasonal_demand_pattern={
                "jan": 0.5, "feb": 0.6, "mar": 0.8, "apr": 1.0,
                "may": 0.7, "jun": 0.6, "jul": 1.5, "aug": 2.5,
                "sep": 2.0, "oct": 1.3, "nov": 1.2, "dec": 1.0
            }
        ),
        
        # Art Supplies
        InventoryItem(
            id="ART_001",
            name="Colored Pencils Set (24 colors)",
            category=StationeryCategory.ART_SUPPLIES,
            current_stock=35,
            min_stock_level=40,
            max_stock_level=150,
            unit_price=24.99,
            supplier="Creative Arts Supply",
            seasonal_demand_pattern={
                "jan": 0.6, "feb": 0.8, "mar": 1.0, "apr": 1.2,
                "may": 0.9, "jun": 0.7, "jul": 1.3, "aug": 2.0,
                "sep": 1.8, "oct": 1.1, "nov": 1.4, "dec": 1.6
            }
        ),
        InventoryItem(
            id="ART_002",
            name="Watercolor Paint Set",
            category=StationeryCategory.ART_SUPPLIES,
            current_stock=12,
            min_stock_level=25,
            max_stock_level=80,
            unit_price=35.75,
            supplier="Artistic Materials Co",
            seasonal_demand_pattern={
                "jan": 0.7, "feb": 0.9, "mar": 1.1, "apr": 1.3,
                "may": 1.0, "jun": 0.8, "jul": 1.4, "aug": 1.9,
                "sep": 1.7, "oct": 1.2, "nov": 1.3, "dec": 1.5
            }
        ),
        
        # Office Supplies
        InventoryItem(
            id="OFF_001",
            name="Stapler Heavy Duty",
            category=StationeryCategory.OFFICE_SUPPLIES,
            current_stock=8,
            min_stock_level=15,
            max_stock_level=50,
            unit_price=28.99,
            supplier="Office Equipment Pro",
            seasonal_demand_pattern={
                "jan": 1.0, "feb": 1.0, "mar": 1.1, "apr": 1.2,
                "may": 1.0, "jun": 0.9, "jul": 1.3, "aug": 1.8,
                "sep": 1.6, "oct": 1.2, "nov": 1.1, "dec": 1.0
            }
        ),
        InventoryItem(
            id="OFF_002",
            name="Paper Clips Box (500 count)",
            category=StationeryCategory.OFFICE_SUPPLIES,
            current_stock=25,
            min_stock_level=30,
            max_stock_level=100,
            unit_price=8.50,
            supplier="Small Office Solutions",
            seasonal_demand_pattern={
                "jan": 0.9, "feb": 1.0, "mar": 1.1, "apr": 1.2,
                "may": 1.1, "jun": 1.0, "jul": 1.4, "aug": 1.9,
                "sep": 1.7, "oct": 1.3, "nov": 1.2, "dec": 1.1
            }
        )
    ]
    return items

def create_sample_sales_data():
    """Create realistic sales data for the last 6 months."""
    sales_data = []
    base_date = datetime.now() - timedelta(days=180)
    
    items = create_sample_inventory()
    
    for i in range(180):  # 6 months of daily data
        current_date = base_date + timedelta(days=i)
        
        for item in items:
            # Seasonal multiplier based on month
            month_key = current_date.strftime("%b").lower()
            seasonal_multiplier = item.seasonal_demand_pattern.get(month_key, 1.0)
            
            # Random daily variation
            daily_variation = random.uniform(0.5, 1.5)
            
            # Base sales quantity (varies by category)
            if item.category == StationeryCategory.BOOKS:
                base_quantity = random.randint(1, 5)
            elif item.category == StationeryCategory.PENS:
                base_quantity = random.randint(3, 15)
            elif item.category == StationeryCategory.NOTEBOOKS:
                base_quantity = random.randint(2, 10)
            elif item.category == StationeryCategory.ART_SUPPLIES:
                base_quantity = random.randint(1, 6)
            else:  # Office supplies
                base_quantity = random.randint(1, 4)
            
            # Calculate final quantity
            final_quantity = max(0, int(base_quantity * seasonal_multiplier * daily_variation))
            
            if final_quantity > 0:  # Only add if there were sales
                sales_data.append(SalesData(
                    id=f"SALE_{current_date.strftime('%Y%m%d')}_{item.id}_{i}",
                    item_id=item.id,
                    quantity_sold=final_quantity,
                    sale_price=item.unit_price * random.uniform(0.95, 1.05),  # Price variation
                    sale_date=current_date,
                    customer_type="retail"
                ))
    
    return sales_data

async def demo_ai_analysis():
    """Demonstrate AI-powered inventory analysis."""
    print("\n" + "="*60)
    print("🤖 AI-POWERED INVENTORY ANALYSIS DEMO")
    print("="*60)
    
    # Create agent
    agent = StationeryInventoryAgent()
    
    # Sample inventory
    inventory = create_sample_inventory()
    sales_history = create_sample_sales_data()
    
    print(f"\n📊 Analyzing {len(inventory)} inventory items...")
    print(f"📈 Using {len(sales_history)} sales data points...")
    
    # Analyze each low-stock item
    for item in inventory:
        if item.current_stock <= item.min_stock_level:
            print(f"\n🔍 Analyzing: {item.name}")
            print(f"   Current Stock: {item.current_stock} (Min: {item.min_stock_level})")
            
            try:
                # Get AI decision
                decision = await agent.create_auto_order_decision(item, sales_history)
                
                print(f"   🤖 AI Decision: {decision.decision_type.value}")
                print(f"   📊 Confidence: {decision.confidence_score:.2%}")
                print(f"   💡 Reasoning: {decision.reasoning[:100]}...")
                print(f"   ⚡ Priority: {decision.priority.value}")
                
                if "order_quantity" in decision.recommended_action:
                    qty = decision.recommended_action["order_quantity"]
                    cost = decision.recommended_action.get("estimated_cost", 0)
                    print(f"   📦 Recommended Order: {qty} units (${cost:.2f})")
                
            except Exception as e:
                print(f"   ❌ Analysis failed: {str(e)}")

async def demo_seasonal_patterns():
    """Demonstrate seasonal pattern recognition."""
    print("\n" + "="*60)
    print("📅 SEASONAL PATTERN RECOGNITION DEMO")
    print("="*60)
    
    agent = StationeryInventoryAgent()
    
    # Test different months
    test_months = [
        (1, "January - Post-holiday period"),
        (3, "March - Mid-term preparations"),
        (6, "June - End of school year"),
        (8, "August - Back-to-school season"),
        (12, "December - Exam period")
    ]
    
    sample_item = create_sample_inventory()[0]  # Mathematics textbook
    
    for month, description in test_months:
        print(f"\n📅 {description}")
        
        analysis = agent.analyze_seasonal_demand(sample_item, month)
        
        print(f"   📊 Demand Multiplier: {analysis['seasonal_multiplier']:.1f}x")
        print(f"   📚 Educational Context: {analysis['educational_context']}")
        print(f"   📈 Demand Level: {analysis['demand_level']}")
        
        if analysis['recommendations']:
            print(f"   💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"      • {rec}")

async def demo_notification_system():
    """Demonstrate the notification system."""
    print("\n" + "="*60)
    print("📱 NOTIFICATION SYSTEM DEMO")
    print("="*60)
    
    print("\n📢 Creating sample notifications...")
    
    # Create different types of notifications
    notifications = [
        NotificationAlert(
            id="NOTIF_001",
            title="Critical Stock Alert",
            message="Mathematics Textbook Grade 10 is critically low (25 units remaining, minimum: 50)",
            alert_type=AlertType.LOW_STOCK,
            priority=Priority.CRITICAL,
            item_id="BOOK_001",
            created_at=datetime.now()
        ),
        NotificationAlert(
            id="NOTIF_002",
            title="Seasonal Demand Warning",
            message="Back-to-school season approaching. Notebook demand expected to increase 300% in 2 weeks.",
            alert_type=AlertType.SEASONAL_ALERT,
            priority=Priority.HIGH,
            created_at=datetime.now()
        ),
        NotificationAlert(
            id="NOTIF_003",
            title="Auto-Order Executed",
            message="Successfully placed order for 200 units of A4 Ruled Notebooks with Paper Products Inc",
            alert_type=AlertType.ORDER_PLACED,
            priority=Priority.MEDIUM,
            item_id="NOTE_001",
            created_at=datetime.now()
        )
    ]
    
    # Display notifications
    for notif in notifications:
        priority_emoji = {
            Priority.CRITICAL: "🚨",
            Priority.HIGH: "⚠️",
            Priority.MEDIUM: "ℹ️",
            Priority.LOW: "📌"
        }
        
        print(f"\n{priority_emoji[notif.priority]} {notif.title}")
        print(f"   📝 {notif.message}")
        print(f"   🏷️  Type: {notif.alert_type.value}")
        print(f"   ⏰ Created: {notif.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if notif.item_id:
            print(f"   📦 Item: {notif.item_id}")

async def demo_database_operations():
    """Demonstrate database operations."""
    print("\n" + "="*60)
    print("💾 DATABASE OPERATIONS DEMO")
    print("="*60)
    
    try:
        # Initialize database
        from app.services.database import init_database
        await init_database()
        
        print("\n✅ Database initialized successfully")
        
        # Sample operations
        inventory = create_sample_inventory()[:3]  # Just first 3 items
        
        print(f"\n📥 Storing {len(inventory)} inventory items...")
        for item in inventory:
            await db_manager.save_inventory_item(item)
        
        print("✅ Inventory items saved")
        
        # Retrieve analytics
        analytics = await db_manager.get_inventory_analytics()
        print(f"\n📊 Inventory Analytics:")
        print(f"   Total Items: {analytics.get('total_items', 0)}")
        print(f"   Total Value: ${analytics.get('total_value', 0):,.2f}")
        print(f"   Low Stock Items: {analytics.get('low_stock_count', 0)}")
        
    except Exception as e:
        print(f"❌ Database demo failed: {str(e)}")
        print("   Note: This is expected if database dependencies are not installed")

async def demo_full_system():
    """Run a comprehensive system demonstration."""
    print("🏪 VERICHAIN STATIONERY INVENTORY MANAGEMENT SYSTEM")
    print("🤖 Complete AI-Powered Demo")
    print("="*80)
    
    # Setup logging
    setup_logging()
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ Dependencies not available - showing limited demo")
        print("   Install dependencies with: uv install")
        return
    
    # Run all demos
    await demo_ai_analysis()
    await demo_seasonal_patterns()
    await demo_notification_system()
    await demo_database_operations()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\n🚀 Key Features Demonstrated:")
    print("   • AI-powered inventory analysis with LangChain + Gemini")
    print("   • Seasonal demand pattern recognition")
    print("   • Educational calendar awareness")
    print("   • Automated decision making with confidence scoring")
    print("   • Real-time notification system")
    print("   • Database persistence and analytics")
    print("   • Production-ready FastAPI integration")
    
    print("\n🌐 To start the full system:")
    print("   python main.py")
    print("   Then visit: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(demo_full_system())