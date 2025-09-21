#!/usr/bin/env python3
"""
Complete API Testing Script for VeriChain Backend
Run this script to test all major API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class VeriChainAPITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.results = {}
    
    async def test_health_check(self):
        """Test basic health check"""
        print("🏥 Testing Health Check...")
        try:
            response = await self.client.get("/health")
            self.results['health'] = {
                'status': response.status_code,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   ✅ Health Check: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"   ❌ Health Check failed: {e}")
            return False
    
    async def test_agent_analysis(self):
        """Test AI agent analysis trigger"""
        print("🤖 Testing AI Agent Analysis...")
        try:
            response = await self.client.post("/api/agent/analyze")
            self.results['agent_analysis'] = {
                'status': response.status_code,
                'data': response.json() if response.status_code in [200, 202] else None
            }
            print(f"   ✅ Agent Analysis: {response.status_code}")
            if response.status_code in [200, 202]:
                print(f"   📊 Analysis Result: {response.json().get('message', 'Processing...')}")
            return True
        except Exception as e:
            print(f"   ❌ Agent Analysis failed: {e}")
            return False
    
    async def test_inventory_endpoints(self):
        """Test inventory management endpoints"""
        print("📦 Testing Inventory Endpoints...")
        
        # Get inventory summary
        try:
            response = await self.client.get("/api/inventory/summary")
            self.results['inventory_summary'] = {
                'status': response.status_code,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   ✅ Inventory Summary: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Total Items: {data.get('total_items', 0)}")
                print(f"   📊 Low Stock Items: {data.get('low_stock_count', 0)}")
        except Exception as e:
            print(f"   ❌ Inventory Summary failed: {e}")
        
        # Get inventory items
        try:
            response = await self.client.get("/api/inventory/items?limit=5")
            self.results['inventory_items'] = {
                'status': response.status_code,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   ✅ Inventory Items: {response.status_code}")
            
            if response.status_code == 200:
                items = response.json()
                print(f"   📦 Retrieved {len(items)} items")
                for item in items[:3]:  # Show first 3 items
                    print(f"      - {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units")
        except Exception as e:
            print(f"   ❌ Inventory Items failed: {e}")
    
    async def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("📊 Testing Dashboard Endpoints...")
        
        dashboards = ['scm', 'finance', 'overview']
        for dashboard in dashboards:
            try:
                response = await self.client.get(f"/api/dashboard/{dashboard}")
                self.results[f'dashboard_{dashboard}'] = {
                    'status': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
                print(f"   ✅ {dashboard.upper()} Dashboard: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      📈 Metrics available: {len(data.keys())}")
            except Exception as e:
                print(f"   ❌ {dashboard.upper()} Dashboard failed: {e}")
    
    async def test_monitoring_endpoints(self):
        """Test monitoring endpoints"""
        print("🔍 Testing Monitoring Endpoints...")
        
        endpoints = [
            ('system/health', 'System Health'),
            ('workflows/active', 'Active Workflows'),
            ('alerts/active', 'Active Alerts')
        ]
        
        for endpoint, name in endpoints:
            try:
                response = await self.client.get(f"/api/monitoring/{endpoint}")
                self.results[f'monitoring_{endpoint.replace("/", "_")}'] = {
                    'status': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
                print(f"   ✅ {name}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"      🔍 Status: {data.get('status', 'Unknown')}")
                    elif isinstance(data, list):
                        print(f"      📊 Count: {len(data)}")
            except Exception as e:
                print(f"   ❌ {name} failed: {e}")
    
    async def test_agent_insights(self):
        """Test getting AI agent insights"""
        print("💡 Testing Agent Insights...")
        try:
            response = await self.client.get("/api/agent/insights")
            self.results['agent_insights'] = {
                'status': response.status_code,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   ✅ Agent Insights: {response.status_code}")
            
            if response.status_code == 200:
                insights = response.json()
                print(f"   🧠 Available insights: {len(insights)}")
                for insight in insights[:2]:  # Show first 2 insights
                    print(f"      - {insight.get('type', 'Unknown')}: {insight.get('summary', 'No summary')}")
        except Exception as e:
            print(f"   ❌ Agent Insights failed: {e}")
    
    async def test_stock_update(self):
        """Test stock update functionality"""
        print("🔄 Testing Stock Update...")
        
        # First get an item to update
        try:
            items_response = await self.client.get("/api/inventory/items?limit=1")
            if items_response.status_code == 200 and items_response.json():
                item = items_response.json()[0]
                item_id = item['id']
                
                # Update stock
                update_data = {
                    "quantity": item['current_stock'] + 50,
                    "reason": "API Test - Stock Replenishment",
                    "updated_by": "api_tester"
                }
                
                response = await self.client.post(
                    f"/api/inventory/items/{item_id}/stock/update",
                    json=update_data
                )
                
                self.results['stock_update'] = {
                    'status': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
                print(f"   ✅ Stock Update: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   📦 Updated {item['name']} stock successfully")
            else:
                print("   ⚠️  No items found to update")
        except Exception as e:
            print(f"   ❌ Stock Update failed: {e}")
    
    async def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting VeriChain API Tests...\n")
        
        # Check if server is running
        if not await self.test_health_check():
            print("❌ Server is not responding. Please ensure the server is running.")
            return
        
        print()
        
        # Run all tests
        await self.test_agent_analysis()
        print()
        
        await self.test_inventory_endpoints()
        print()
        
        await self.test_dashboard_endpoints()
        print()
        
        await self.test_monitoring_endpoints()
        print()
        
        await self.test_agent_insights()
        print()
        
        await self.test_stock_update()
        print()
        
        # Summary
        print("📋 Test Summary:")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() 
                             if result['status'] in [200, 201, 202])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅" if result['status'] in [200, 201, 202] else "❌"
            print(f"  {status} {test_name}: HTTP {result['status']}")
        
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = VeriChainAPITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())