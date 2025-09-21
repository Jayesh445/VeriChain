#!/usr/bin/env python3
"""
Quick API test script to verify all endpoints are working
"""

import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000"

endpoints_to_test = [
    "/api/sales/analytics?days=30",
    "/api/agent/insights?role=admin&limit=20",
    "/api/agent/decisions/recent?limit=20",
    "/api/dashboard/scm",
    "/api/dashboard/finance",
    "/api/inventory/summary",
    "/api/inventory/items"
]

async def test_endpoint(session, endpoint):
    """Test a single API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ {endpoint} - OK ({len(str(data))} chars)")
                return True
            else:
                text = await response.text()
                print(f"❌ {endpoint} - Status {response.status}: {text}")
                return False
    except Exception as e:
        print(f"❌ {endpoint} - Error: {str(e)}")
        return False

async def main():
    """Test all endpoints"""
    print("🚀 Testing VeriChain API endpoints...")
    print(f"API Base: {API_BASE}")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        results = []
        for endpoint in endpoints_to_test:
            result = await test_endpoint(session, endpoint)
            results.append(result)
        
        success_count = sum(results)
        total_count = len(results)
        
        print("-" * 50)
        print(f"📊 Results: {success_count}/{total_count} endpoints working")
        
        if success_count == total_count:
            print("🎉 All endpoints are working correctly!")
        else:
            print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    asyncio.run(main())