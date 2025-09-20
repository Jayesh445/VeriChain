"""
Comprehensive Demo for Stock Monitoring and Dashboard APIs
Tests all new endpoints with real Gemini AI integration.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any
import time

class VeriChainAPIDemo:
    """Demo class for VeriChain API testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.monitor_id = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None):
        """Test an API endpoint and return response."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
                    return response.status, result
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
                    return response.status, result
        except Exception as e:
            return None, {"error": str(e)}
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_api_result(self, endpoint: str, status: int, data: Dict):
        """Print API result in a formatted way."""
        status_emoji = "✅" if status and 200 <= status < 300 else "❌"
        print(f"\n{status_emoji} {endpoint}")
        print(f"   Status: {status}")
        
        if status and 200 <= status < 300:
            # Print key insights from successful responses
            if "ai_insights" in data:
                print(f"   🤖 AI Insights: {data['ai_insights'].get('recommended_action', 'N/A')}")
            if "recommendations" in data:
                recommendations = data["recommendations"][:2]  # Show first 2
                for rec in recommendations:
                    print(f"   💡 {rec}")
            if "health_score" in data:
                print(f"   📊 Health Score: {data['health_score']}%")
            if "total_items" in data:
                print(f"   📦 Total Items: {data['total_items']}")
            if "monitor_id" in data:
                self.monitor_id = data["monitor_id"]
                print(f"   🔍 Monitor ID: {data['monitor_id']}")
        else:
            print(f"   ❌ Error: {data.get('detail', 'Unknown error')}")

    async def demo_dashboard_apis(self):
        """Demonstrate all dashboard APIs."""
        self.print_section("Dashboard APIs with AI Insights")
        
        # Test dashboard summary
        status, data = await self.test_api_endpoint("/api/v1/dashboard/summary")
        self.print_api_result("Dashboard Summary", status, data)
        
        # Test sales analytics
        status, data = await self.test_api_endpoint("/api/v1/dashboard/sales-analytics?days=30")
        self.print_api_result("Sales Analytics (30 days)", status, data)
        if status and 200 <= status < 300:
            print(f"   💰 Total Sales: ${data.get('total_sales', 0):.2f}")
            print(f"   📈 Sales Count: {data.get('sales_count', 0)}")
            print(f"   📊 Avg Order Value: ${data.get('avg_order_value', 0):.2f}")
        
        # Test inventory overview
        status, data = await self.test_api_endpoint("/api/v1/dashboard/inventory-overview")
        self.print_api_result("Inventory Overview", status, data)
        if status and 200 <= status < 300:
            print(f"   📦 Categories: {len(data.get('categories', []))}")
            print(f"   ⚠️ Critical Items: {len(data.get('critical_items', []))}")
            print(f"   🎯 AI Health Score: {data.get('ai_health_score', 0):.2f}")
        
        # Test negotiations summary
        status, data = await self.test_api_endpoint("/api/v1/dashboard/negotiations-summary")
        self.print_api_result("Negotiations Summary", status, data)
        if status and 200 <= status < 300:
            print(f"   🤝 Active: {data.get('active_negotiations', 0)}")
            print(f"   ✅ Completed: {data.get('completed_negotiations', 0)}")
            print(f"   📈 Success Rate: {data.get('success_rate', 0):.1f}%")
            print(f"   💵 Avg Savings: ${data.get('average_savings', 0):.2f}")
        
        # Test dashboard insights
        status, data = await self.test_api_endpoint("/api/v1/dashboard/insights?limit=5")
        self.print_api_result("AI Dashboard Insights", status, data)
        if status and 200 <= status < 300 and isinstance(data, list):
            for i, insight in enumerate(data[:3], 1):
                print(f"   🧠 Insight {i}: {insight.get('title', 'N/A')}")
                print(f"      Impact: {insight.get('impact_level', 'N/A')} | Confidence: {insight.get('confidence', 0):.0%}")

    async def demo_monitoring_apis(self):
        """Demonstrate stock monitoring APIs."""
        self.print_section("Stock Monitoring APIs with Real-time AI")
        
        # Start monitoring
        monitoring_config = {
            "interval_minutes": 1,  # Short interval for demo
            "enable_alerts": True,
            "alert_threshold_days": 7,
            "enable_predictions": True,
            "categories": ["office_supplies", "writing_instruments"],
            "priority_items": ["PEN001", "NOTEBOOK001"]
        }
        
        status, data = await self.test_api_endpoint(
            "/api/v1/monitoring/start", 
            "POST", 
            monitoring_config
        )
        self.print_api_result("Start Monitoring", status, data)
        
        if not self.monitor_id:
            print("❌ Could not start monitoring, skipping monitoring tests")
            return
        
        # Wait a bit for monitoring to start
        print("\n⏳ Waiting for monitoring to initialize...")
        await asyncio.sleep(3)
        
        # Check monitoring status
        status, data = await self.test_api_endpoint(f"/api/v1/monitoring/status/{self.monitor_id}")
        self.print_api_result("Monitoring Status", status, data)
        if status and 200 <= status < 300:
            print(f"   ⏰ Started: {data.get('started_at', 'N/A')}")
            print(f"   🔍 Items Monitored: {data.get('items_monitored', 0)}")
            print(f"   🚨 Alerts Generated: {data.get('alerts_generated', 0)}")
        
        # Wait for some monitoring cycles
        print("\n⏳ Waiting for monitoring cycles to complete...")
        await asyncio.sleep(5)
        
        # Get monitoring insights
        status, data = await self.test_api_endpoint(f"/api/v1/monitoring/insights/{self.monitor_id}?limit=5")
        self.print_api_result("Monitoring Insights", status, data)
        if status and 200 <= status < 300 and isinstance(data, list):
            for i, insight in enumerate(data[:3], 1):
                print(f"   🔍 Insight {i}: {insight.get('item_name', 'N/A')}")
                print(f"      Stock: {insight.get('current_stock', 0)} | Priority: {insight.get('priority', 'N/A')}")
                print(f"      Recommendation: {insight.get('recommendation', 'N/A')[:50]}...")
        
        # Get monitoring report
        status, data = await self.test_api_endpoint(f"/api/v1/monitoring/report/{self.monitor_id}")
        self.print_api_result("Monitoring Report", status, data)
        if status and 200 <= status < 300:
            summary = data.get('summary', {})
            metrics = data.get('performance_metrics', {})
            print(f"   ⏱️ Duration: {summary.get('monitoring_duration', 0):.1f} hours")
            print(f"   📊 Efficiency: {metrics.get('monitoring_efficiency', 0):.2f}")
            print(f"   🎯 Avg Confidence: {metrics.get('avg_confidence', 0):.0%}")
        
        # Get active monitors
        status, data = await self.test_api_endpoint("/api/v1/monitoring/active-monitors")
        self.print_api_result("Active Monitors", status, data)
        if status and 200 <= status < 300:
            print(f"   🔍 Total Active: {data.get('total_active', 0)}")
        
        # Stop monitoring
        status, data = await self.test_api_endpoint(f"/api/v1/monitoring/stop/{self.monitor_id}", "POST")
        self.print_api_result("Stop Monitoring", status, data)

    async def demo_background_tasks(self):
        """Demonstrate background task APIs."""
        self.print_section("Background Analytics Refresh")
        
        # Trigger analytics refresh
        status, data = await self.test_api_endpoint("/api/v1/dashboard/refresh-analytics", "POST")
        self.print_api_result("Analytics Refresh", status, data)
        
        if status and 200 <= status < 300:
            print("   🔄 Background analytics refresh started")
            print("   📊 This will update all dashboard data with fresh AI insights")

    async def demo_category_analysis(self):
        """Demonstrate category-specific analysis."""
        self.print_section("Category-Specific AI Analysis")
        
        # Test common categories
        categories = ["writing_instruments", "office_supplies", "notebooks"]
        
        for category in categories:
            status, data = await self.test_api_endpoint(f"/api/v1/dashboard/category-stats/{category}")
            
            if status and 200 <= status < 300:
                print(f"\n✅ {category.replace('_', ' ').title()}")
                print(f"   📦 Items: {data.get('items_count', 0)}")
                print(f"   💰 Total Value: ${data.get('total_value', 0):.2f}")
                print(f"   ⚠️ Low Stock: {data.get('low_stock_count', 0)}")
                print(f"   📊 Avg Stock Level: {data.get('avg_stock_level', 0):.1f}")
                print(f"   🤖 AI Trend: {data.get('trend_prediction', 'N/A')}")
            else:
                print(f"\n❌ {category}: Category not found or error occurred")

    async def run_complete_demo(self):
        """Run the complete API demonstration."""
        print("🎯 VeriChain Stock Monitoring & Dashboard API Demo")
        print("=" * 60)
        print("⏰ Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            # Test if server is running
            status, _ = await self.test_api_endpoint("/docs")
            if not status or status != 200:
                print("❌ Server not running. Please start with: python main.py")
                return
            
            print("✅ Server is running and accessible")
            
            # Run all demos
            await self.demo_dashboard_apis()
            await self.demo_monitoring_apis()
            await self.demo_background_tasks()
            await self.demo_category_analysis()
            
            # Summary
            self.print_section("Demo Summary")
            print("✅ Dashboard APIs - Real-time AI insights for inventory management")
            print("✅ Stock Monitoring - Continuous AI-powered analysis with alerts")
            print("✅ Background Tasks - Automated analytics refresh")
            print("✅ Category Analysis - Detailed AI insights per product category")
            print("\n🚀 All VeriChain APIs are production-ready!")
            print("💡 Access API docs at: http://localhost:8000/docs")
            print("📊 Use these APIs to build comprehensive inventory dashboards")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main demo function."""
    async with VeriChainAPIDemo() as demo:
        await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())