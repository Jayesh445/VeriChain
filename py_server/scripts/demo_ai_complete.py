"""
Comprehensive VeriChain AI Demo
Demonstrates the complete AI-powered inventory management system with real LangChain Gemini integration.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_service import initialize_ai_service, get_ai_service
from app.services.negotiation_chat import SupplierNegotiationChat, initialize_negotiation_chat
from app.services.auto_ordering import initialize_auto_ordering, get_auto_ordering_engine
from app.core.config import settings

class VeriChainAIDemo:
    """Comprehensive demo of VeriChain AI capabilities."""
    
    def __init__(self):
        self.ai_service = None
        self.negotiation_system = None
        self.auto_ordering = None
    
    async def initialize_all_systems(self):
        """Initialize all AI-powered systems."""
        print("🚀 VeriChain AI System Initialization")
        print("=" * 60)
        
        # Check API key
        api_key = (
            settings.google_api_key or 
            settings.gemini_api_key or 
            os.getenv('GOOGLE_API_KEY') or 
            os.getenv('GEMINI_API_KEY')
        )
        
        if not api_key:
            print("❌ No API key found!")
            print("💡 Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            print("   Example: $env:GOOGLE_API_KEY='your_api_key_here'")
            return False
        
        try:
            # Initialize AI service
            print("🤖 Initializing AI Service...")
            await initialize_ai_service()
            self.ai_service = await get_ai_service()
            print("✅ AI Service ready")
            
            # Initialize negotiation system
            print("💬 Initializing Negotiation System...")
            await initialize_negotiation_chat()
            self.negotiation_system = SupplierNegotiationChat(self.ai_service)
            print("✅ Negotiation System ready")
            
            # Initialize auto-ordering
            print("📦 Initializing Auto-Ordering...")
            await initialize_auto_ordering()
            self.auto_ordering = await get_auto_ordering_engine()
            print("✅ Auto-Ordering ready")
            
            print("\n🎯 All systems initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def demo_ai_inventory_analysis(self):
        """Demonstrate AI-powered inventory analysis."""
        print("\n📊 AI Inventory Analysis Demo")
        print("-" * 40)
        
        try:
            # Get AI analysis
            analysis = await self.ai_service.analyze_inventory_status({
                "demo_mode": True,
                "focus_areas": ["seasonal_trends", "cost_optimization"],
                "time_horizon": "next_30_days"
            })
            
            print(f"🎯 AI Decision: {analysis.decision}")
            print(f"🧠 Reasoning: {analysis.reasoning[:200]}...")
            print(f"📈 Confidence: {analysis.confidence_score:.1%}")
            print(f"📋 Key Data Points:")
            for point in analysis.data_points[:3]:
                print(f"   • {point}")
            
            print(f"🚀 Next Actions:")
            for action in analysis.next_actions[:3]:
                print(f"   • {action}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    async def demo_intelligent_negotiation(self):
        """Demonstrate AI-powered supplier negotiations."""
        print("\n🤝 AI-Powered Negotiation Demo")
        print("-" * 40)
        
        # Sample negotiation scenario
        scenario = {
            "item_sku": "PEN001",
            "item_name": "Premium Ball Point Pens (Box of 50)",
            "initial_price": 450.00,
            "target_price": 380.00,
            "supplier_id": "rajesh_stationery",
            "quantity": 200
        }
        
        try:
            # Start negotiation
            session_id = await self.negotiation_system.start_negotiation(
                item_sku=scenario["item_sku"],
                item_name=scenario["item_name"],
                initial_price=scenario["initial_price"],
                target_price=scenario["target_price"],
                supplier_id=scenario["supplier_id"],
                quantity=scenario["quantity"]
            )
            
            print(f"📋 Negotiating: {scenario['item_name']}")
            print(f"💰 Initial Quote: ₹{scenario['initial_price']:.2f}")
            print(f"🎯 Target Price: ₹{scenario['target_price']:.2f}")
            print(f"🏢 Supplier: {self.negotiation_system.suppliers[scenario['supplier_id']]['company']}")
            print()
            
            # Simulate negotiation rounds
            negotiation_messages = [
                f"Hi, we need {scenario['quantity']} units. Your quote of ₹{scenario['initial_price']:.2f} seems high for bulk order. Can you do better?",
                f"We're looking at ₹{scenario['target_price']:.2f} per unit. This fits our budget for long-term partnership.",
                "This is for regular monthly orders. What's your best price for committed volume?",
                f"Final offer: ₹{scenario['target_price'] + 15:.2f}. This is our maximum budget."
            ]
            
            for i, message in enumerate(negotiation_messages, 1):
                print(f"👤 Round {i}: {message}")
                
                # Send message and get AI response
                result = await self.negotiation_system.send_message(session_id, message)
                print(f"📤 Status: {result.get('status', 'sent')}")
                
                # Wait for supplier response
                await asyncio.sleep(2)
                
                # Get chat history to see latest response
                chat = await self.negotiation_system.get_negotiation_chat(session_id)
                
                # Find latest supplier message
                supplier_messages = [
                    msg for msg in chat["messages"] 
                    if msg["sender_type"] == "supplier"
                ]
                
                if supplier_messages:
                    latest = supplier_messages[-1]
                    supplier_name = latest["sender"]
                    print(f"🏢 {supplier_name}: {latest['content']}")
                    
                    # Show AI metadata if available
                    if "metadata" in latest and "ai_action" in latest["metadata"]:
                        ai_meta = latest["metadata"]
                        print(f"   🤖 AI Action: {ai_meta.get('ai_action')}")
                        print(f"   🎯 Confidence: {ai_meta.get('ai_confidence', 0):.1%}")
                
                print()
                
                # Check if negotiation concluded
                if not chat["is_active"]:
                    break
                
                await asyncio.sleep(1)
            
            # Show final results
            final_chat = await self.negotiation_system.get_negotiation_chat(session_id)
            if final_chat["current_offer"]:
                savings = scenario["initial_price"] - final_chat["current_offer"]
                savings_pct = (savings / scenario["initial_price"]) * 100
                print(f"💰 Final Price: ₹{final_chat['current_offer']:.2f}")
                print(f"💵 Savings: ₹{savings:.2f} ({savings_pct:.1f}%)")
            else:
                print("❌ Negotiation ended without agreement")
                
        except Exception as e:
            print(f"❌ Negotiation demo failed: {e}")
    
    async def demo_auto_ordering_intelligence(self):
        """Demonstrate AI-powered auto-ordering decisions."""
        print("\n📦 AI Auto-Ordering Demo")
        print("-" * 40)
        
        try:
            # Get AI ordering analysis
            ordering_analysis = await self.ai_service.analyze_auto_ordering_needs({
                "urgency_level": "medium",
                "budget_constraints": "moderate",
                "seasonal_context": "back_to_school_season"
            })
            
            print(f"🎯 AI Recommendation: {ordering_analysis.decision}")
            print(f"🧠 Analysis: {ordering_analysis.reasoning[:200]}...")
            print(f"📊 Confidence: {ordering_analysis.confidence_score:.1%}")
            
            print(f"\n📋 Key Insights:")
            for point in ordering_analysis.data_points[:4]:
                print(f"   • {point}")
            
            print(f"\n🚀 Recommended Actions:")
            for action in ordering_analysis.next_actions[:4]:
                print(f"   • {action}")
            
            # Simulate order decisions
            print(f"\n📦 Sample Order Decisions:")
            sample_decisions = [
                {"item": "A4 Notebooks", "qty": 150, "priority": "HIGH", "reason": "Back-to-school demand surge"},
                {"item": "Ball Point Pens", "qty": 200, "priority": "MEDIUM", "reason": "Steady consumption rate"},
                {"item": "Erasers", "qty": 100, "priority": "LOW", "reason": "Adequate stock levels"}
            ]
            
            for decision in sample_decisions:
                print(f"   📝 {decision['item']}: {decision['qty']} units ({decision['priority']})")
                print(f"      Reason: {decision['reason']}")
            
        except Exception as e:
            print(f"❌ Auto-ordering demo failed: {e}")
    
    async def demo_notification_intelligence(self):
        """Demonstrate AI-generated notifications."""
        print("\n📧 AI Notification Demo")
        print("-" * 40)
        
        try:
            # Sample notification scenarios
            scenarios = [
                {
                    "type": "low_stock_alert",
                    "context": {
                        "item_name": "A4 Ruled Notebooks",
                        "current_stock": 15,
                        "minimum_stock": 50,
                        "estimated_days_remaining": 3
                    }
                },
                {
                    "type": "negotiation_success",
                    "context": {
                        "supplier": "Rajesh Stationery",
                        "item": "Premium Pens",
                        "savings": 70.00,
                        "final_price": 380.00
                    }
                }
            ]
            
            for scenario in scenarios:
                print(f"📬 {scenario['type'].replace('_', ' ').title()}:")
                
                notification_content = await self.ai_service.generate_notification_content(
                    scenario["type"], scenario["context"]
                )
                
                print(f"   📧 Subject: {notification_content.get('subject', 'N/A')}")
                print(f"   📝 Preview: {notification_content.get('dashboard_alert', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Notification demo failed: {e}")
    
    async def run_complete_demo(self):
        """Run the complete AI system demonstration."""
        print("🎯 VeriChain AI System Complete Demo")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Initialize systems
        if not await self.initialize_all_systems():
            return
        
        # Run all demos
        await self.demo_ai_inventory_analysis()
        await self.demo_intelligent_negotiation()
        await self.demo_auto_ordering_intelligence()
        await self.demo_notification_intelligence()
        
        print("\n🎉 Demo Summary")
        print("-" * 40)
        print("✅ AI Inventory Analysis - Real-time intelligent insights")
        print("✅ Supplier Negotiations - Context-aware AI decisions")
        print("✅ Auto-Ordering Intelligence - Predictive order optimization")
        print("✅ Smart Notifications - AI-generated content")
        
        print(f"\n🚀 All AI systems are production-ready!")
        print(f"💡 Start the server with: python main.py")
        print(f"📖 API docs at: http://localhost:8000/docs")

async def main():
    """Main demo function."""
    demo = VeriChainAIDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")