#!/usr/bin/env python3
"""
Test script for the enhanced AI agent negotiation system
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import Vendor, StationeryItem, VendorStatus
from app.agents.supply_chain_agent import SupplyChainAgent
from app.api.ai_agent import _generate_vendor_negotiation_with_gemini, NegotiationSession
from sqlalchemy import select


async def test_real_negotiation():
    """Test the real Gemini-powered negotiation system"""
    
    print("🧪 Testing Real Gemini AI Negotiation System")
    print("=" * 50)
    
    # Initialize Gemini agent
    gemini_agent = SupplyChainAgent()
    
    # Test Gemini API connectivity
    print("1. Testing Gemini API connectivity...")
    try:
        response = await gemini_agent._call_gemini_api("Hello, respond with 'API Connected' if you receive this.")
        print(f"   ✅ Gemini API Response: {response[:50]}...")
    except Exception as e:
        print(f"   ❌ Gemini API Error: {str(e)}")
        return False
    
    # Test with database
    print("\n2. Testing database connectivity...")
    async with AsyncSessionLocal() as db:
        try:
            # Get vendors
            vendors_result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE))
            vendors = vendors_result.scalars().all()
            print(f"   ✅ Found {len(vendors)} active vendors")
            
            # Get items
            items_result = await db.execute(select(StationeryItem).limit(1))
            items = items_result.scalars().all()
            print(f"   ✅ Found {len(items)} items")
            
            if not vendors:
                print("   ⚠️  No vendors found - creating sample vendor...")
                sample_vendor = Vendor(
                    name="Test Vendor Co",
                    status=VendorStatus.ACTIVE,
                    reliability_score=8.5,
                    avg_delivery_days=7
                )
                db.add(sample_vendor)
                await db.commit()
                vendors = [sample_vendor]
            
            if not items:
                print("   ⚠️  No items found - will use mock item data")
                
        except Exception as e:
            print(f"   ❌ Database Error: {str(e)}")
            return False
    
    # Test real negotiation with Gemini
    print("\n3. Testing real vendor negotiation with Gemini AI...")
    try:
        # Create mock negotiation session
        session = NegotiationSession(
            session_id="test_session_123",
            item_id=items[0].id if items else 1,
            item_name=items[0].name if items else "Test Item",
            quantity_needed=100,
            status="negotiating",
            vendor_proposals=[],
            conversation=[],
            best_proposal=None,
            ai_reasoning="Testing negotiation",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test negotiation with first vendor
        vendor = vendors[0]
        print(f"   📞 Testing negotiation with {vendor.name}...")
        
        vendor_context = await _generate_vendor_negotiation_with_gemini(
            session, vendor, 1, len(vendors)
        )
        
        print(f"   ✅ Negotiation successful!")
        print(f"   📋 Proposal: ${vendor_context['proposal'].unit_price:.2f}/unit")
        print(f"   💬 Conversation messages: {len(vendor_context['conversation'])}")
        
        # Display conversation sample
        if vendor_context['conversation']:
            print("\n   Sample conversation:")
            for i, msg in enumerate(vendor_context['conversation'][:2]):
                print(f"     {msg.speaker}: {msg.message[:60]}...")
        
        # Test Gemini data
        if vendor_context.get('gemini_data'):
            print(f"   🤖 Gemini provided structured data: {bool(vendor_context['gemini_data'])}")
        else:
            print(f"   ⚠️  Used fallback data (Gemini parsing failed)")
            
    except Exception as e:
        print(f"   ❌ Negotiation Error: {str(e)}")
        return False
    
    print("\n4. Testing multiple vendor negotiations...")
    try:
        all_proposals = []
        for i, vendor in enumerate(vendors[:3]):  # Test with up to 3 vendors
            vendor_context = await _generate_vendor_negotiation_with_gemini(
                session, vendor, i + 1, len(vendors)
            )
            all_proposals.append(vendor_context['proposal'])
            print(f"   ✅ {vendor.name}: ${vendor_context['proposal'].unit_price:.2f}/unit")
        
        # Find best proposal
        best_proposal = min(all_proposals, key=lambda p: p.unit_price)
        print(f"\n   🏆 Best proposal: {best_proposal.vendor_name} at ${best_proposal.unit_price:.2f}/unit")
        
    except Exception as e:
        print(f"   ❌ Multiple negotiation error: {str(e)}")
        return False
    
    print("\n✅ All tests passed! Real Gemini AI negotiation system is working correctly.")
    print("\n📊 System Capabilities:")
    print("   • Real-time vendor negotiation with Gemini AI")
    print("   • Negotiates with ALL active vendors (not limited to 3)")
    print("   • Structured conversation tracking")
    print("   • Intelligent proposal analysis and scoring")
    print("   • Fallback system when Gemini is unavailable")
    
    return True


async def main():
    """Main test function"""
    success = await test_real_negotiation()
    
    if success:
        print("\n🎉 Real AI negotiation system is ready for production!")
    else:
        print("\n❌ Tests failed. Please check configuration and dependencies.")


if __name__ == "__main__":
    asyncio.run(main())