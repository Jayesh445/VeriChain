#!/usr/bin/env python3
"""
Sample Data Creation Script
Creates realistic test data for the VeriChain system
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

class DataCreator:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
    
    async def create_sample_sales(self):
        """Create sample sales records"""
        print("💰 Creating Sample Sales Records...")
        
        # Sample sales data
        sales_data = [
            {
                "item_id": 1,
                "quantity_sold": 25,
                "unit_price": 1.20,
                "total_amount": 30.00,
                "customer_type": "INTERNAL",
                "department": "HR",
                "sale_date": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "item_id": 2,
                "quantity_sold": 15,
                "unit_price": 0.85,
                "total_amount": 12.75,
                "customer_type": "INTERNAL",
                "department": "Finance",
                "sale_date": (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "item_id": 3,
                "quantity_sold": 50,
                "unit_price": 0.05,
                "total_amount": 2.50,
                "customer_type": "INTERNAL",
                "department": "Marketing",
                "sale_date": (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                "item_id": 4,
                "quantity_sold": 10,
                "unit_price": 2.50,
                "total_amount": 25.00,
                "customer_type": "EXTERNAL",
                "department": "Sales",
                "sale_date": (datetime.now() - timedelta(days=4)).isoformat()
            },
            {
                "item_id": 5,
                "quantity_sold": 8,
                "unit_price": 15.99,
                "total_amount": 127.92,
                "customer_type": "INTERNAL",
                "department": "IT",
                "sale_date": (datetime.now() - timedelta(days=5)).isoformat()
            }
        ]
        
        for sale in sales_data:
            try:
                response = await self.client.post("/api/sales/record", json=sale)
                if response.status_code in [200, 201]:
                    print(f"   ✅ Created sale for item {sale['item_id']}: {sale['quantity_sold']} units")
                else:
                    print(f"   ❌ Failed to create sale: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error creating sale: {e}")
    
    async def create_sample_orders(self):
        """Create sample purchase orders"""
        print("📋 Creating Sample Purchase Orders...")
        
        orders_data = [
            {
                "vendor_id": 1,
                "order_items": [
                    {"item_id": 1, "quantity": 100, "unit_price": 1.15},
                    {"item_id": 2, "quantity": 200, "unit_price": 0.80}
                ],
                "priority": "HIGH",
                "notes": "Urgent restock for ballpoint pens and pencils"
            },
            {
                "vendor_id": 2,
                "order_items": [
                    {"item_id": 3, "quantity": 500, "unit_price": 0.04},
                    {"item_id": 4, "quantity": 50, "unit_price": 2.25}
                ],
                "priority": "NORMAL",
                "notes": "Monthly paper supplies order"
            },
            {
                "vendor_id": 3,
                "order_items": [
                    {"item_id": 5, "quantity": 25, "unit_price": 14.99}
                ],
                "priority": "LOW",
                "notes": "Office calculator replacement"
            }
        ]
        
        for order in orders_data:
            try:
                response = await self.client.post("/api/orders", json=order)
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"   ✅ Created order {data.get('id', 'Unknown')} for vendor {order['vendor_id']}")
                else:
                    print(f"   ❌ Failed to create order: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error creating order: {e}")
    
    async def update_stock_levels(self):
        """Update stock levels to create realistic scenarios"""
        print("📦 Updating Stock Levels...")
        
        stock_updates = [
            {"item_id": 1, "quantity": 45, "reason": "Low stock simulation"},
            {"item_id": 2, "quantity": 15, "reason": "Critical stock level"},
            {"item_id": 3, "quantity": 125, "reason": "Normal restocking"},
            {"item_id": 4, "quantity": 8, "reason": "Below reorder point"},
            {"item_id": 5, "quantity": 22, "reason": "Standard inventory"}
        ]
        
        for update in stock_updates:
            try:
                update_data = {
                    "quantity": update["quantity"],
                    "reason": update["reason"],
                    "updated_by": "data_creator"
                }
                
                response = await self.client.post(
                    f"/api/inventory/items/{update['item_id']}/stock/update",
                    json=update_data
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Updated item {update['item_id']} to {update['quantity']} units")
                else:
                    print(f"   ❌ Failed to update item {update['item_id']}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error updating stock: {e}")
    
    async def create_additional_vendors(self):
        """Add more vendors for testing"""
        print("🏢 Creating Additional Vendors...")
        
        vendors_data = [
            {
                "name": "EcoFriendly Office Supplies",
                "contact_person": "Sarah Green",
                "email": "sarah@ecooffice.com",
                "phone": "+1-555-0199",
                "address": "456 Green Street, Eco City, EC 67890",
                "rating": 4.2,
                "is_active": True
            },
            {
                "name": "Budget Stationery Mart",
                "contact_person": "Mike Johnson",
                "email": "mike@budgetmart.com",
                "phone": "+1-555-0177",
                "address": "789 Budget Ave, Savings Town, ST 13579",
                "rating": 3.8,
                "is_active": True
            }
        ]
        
        for vendor in vendors_data:
            try:
                response = await self.client.post("/api/vendors", json=vendor)
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"   ✅ Created vendor: {vendor['name']}")
                else:
                    print(f"   ❌ Failed to create vendor: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error creating vendor: {e}")
    
    async def create_inventory_items(self):
        """Add more inventory items"""
        print("📝 Creating Additional Inventory Items...")
        
        items_data = [
            {
                "name": "Gel Pen (Blue)",
                "description": "Smooth gel ink pen in blue color",
                "category": "WRITING_INSTRUMENTS",
                "current_stock": 80,
                "reorder_level": 15,
                "max_stock": 300,
                "unit_price": 1.75,
                "unit": "piece",
                "vendor_id": 1
            },
            {
                "name": "Whiteboard Marker Set",
                "description": "Set of 4 colored whiteboard markers",
                "category": "WRITING_INSTRUMENTS",
                "current_stock": 25,
                "reorder_level": 8,
                "max_stock": 100,
                "unit_price": 8.99,
                "unit": "set",
                "vendor_id": 2
            },
            {
                "name": "Legal Size Paper",
                "description": "8.5x14 inch legal size white paper",
                "category": "PAPER_PRODUCTS",
                "current_stock": 200,
                "reorder_level": 50,
                "max_stock": 1000,
                "unit_price": 12.99,
                "unit": "ream",
                "vendor_id": 1
            },
            {
                "name": "Desk Organizer Tray",
                "description": "Multi-compartment plastic desk organizer",
                "category": "DESK_ACCESSORIES",
                "current_stock": 12,
                "reorder_level": 5,
                "max_stock": 50,
                "unit_price": 24.99,
                "unit": "piece",
                "vendor_id": 3
            }
        ]
        
        for item in items_data:
            try:
                response = await self.client.post("/api/inventory/items", json=item)
                if response.status_code in [200, 201]:
                    print(f"   ✅ Created item: {item['name']}")
                else:
                    print(f"   ❌ Failed to create item: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error creating item: {e}")
    
    async def run_data_creation(self):
        """Run all data creation tasks"""
        print("🚀 Starting Sample Data Creation...\n")
        
        # Check if server is running
        try:
            response = await self.client.get("/health")
            if response.status_code != 200:
                print("❌ Server is not responding. Please ensure the server is running.")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return
        
        print("✅ Server is running. Creating sample data...\n")
        
        # Create data in logical order
        await self.create_additional_vendors()
        print()
        
        await self.create_inventory_items()
        print()
        
        await self.update_stock_levels()
        print()
        
        await self.create_sample_sales()
        print()
        
        await self.create_sample_orders()
        print()
        
        print("✅ Sample data creation completed!")
        print("\n🎯 Next Steps:")
        print("1. Run: python scripts/test_api_complete.py")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test AI Agent: curl -X POST http://localhost:8000/api/agent/analyze")
        
        await self.client.aclose()

async def main():
    creator = DataCreator()
    await creator.run_data_creation()

if __name__ == "__main__":
    asyncio.run(main())