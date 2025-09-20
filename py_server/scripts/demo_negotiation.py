"""
Demo script for VeriChain Supplier Negotiation Chat System
Shows real-time AI-powered negotiations with suppliers using LangChain Gemini.
"""

import asyncio
import json
import os
from datetime import datetime
from app.services.ai_service import get_ai_service, initialize_ai_service
from app.services.negotiation_chat import SupplierNegotiationChat

async def demo_negotiation_system():
    """Demonstrate the AI-powered negotiation system."""
    
    print("🤝 VeriChain Supplier Negotiation Chat System Demo")
    print("=" * 60)
    
    print("🤖 Initializing VeriChain AI Service...")
    try:
        # Initialize AI service
        await initialize_ai_service()
        ai_service = await get_ai_service()
        print("✅ VeriChain AI Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI Service: {e}")
        print("💡 Make sure GOOGLE_API_KEY or GEMINI_API_KEY is set in your environment")
        return
    
    # Initialize negotiation chat system with AI service
    chat_system = SupplierNegotiationChat(ai_service)
    
    print("🏢 Available Suppliers:")
    for supplier_id, supplier in chat_system.suppliers.items():
        print(f"   • {supplier['company']} ({supplier['name']}) - {supplier['personality']['name']}")
    print()
    
    # Demo scenarios
    scenarios = [
        {
            "item_sku": "PEN001",
            "item_name": "Premium Ball Point Pens (Box of 50)",
            "initial_price": 450.00,
            "target_price": 380.00,
            "supplier_id": "rajesh_stationery",
            "quantity": 200
        },
        {
            "item_sku": "NOTE001",
            "item_name": "A4 Ruled Notebooks (Pack of 10)",
            "initial_price": 280.00,
            "target_price": 240.00,
            "supplier_id": "modern_office", 
            "quantity": 150
        }
    ]
    
    # Run demo negotiations
    for i, scenario in enumerate(scenarios, 1):
        print(f"📋 Demo Scenario {i}: {scenario['item_name']}")
        print(f"   Initial Quote: ₹{scenario['initial_price']:.2f}")
        print(f"   Target Price: ₹{scenario['target_price']:.2f}")
        print(f"   Supplier: {chat_system.suppliers[scenario['supplier_id']]['company']}")
        print()
        
        # Start negotiation
        session_id = await chat_system.start_negotiation(
            item_sku=scenario["item_sku"],
            item_name=scenario["item_name"],
            initial_price=scenario["initial_price"],
            target_price=scenario["target_price"],
            supplier_id=scenario["supplier_id"],
            quantity=scenario["quantity"]
        )
        
        print(f"💬 Negotiation Started (Session: {session_id})")
        
        # Simulate some negotiation rounds
        user_messages = [
            f"Hi, we need {scenario['quantity']} units of {scenario['item_name']}. Your quote of ₹{scenario['initial_price']:.2f} seems high. Can you do better?",
            f"We're looking at ₹{scenario['target_price']:.2f} per unit for this volume. Can you match this?",
            "This is for a long-term partnership. We'll have regular orders if pricing works out.",
            f"Final offer: ₹{scenario['target_price'] + 10:.2f}. This is our budget limit."
        ]
        
        for msg in user_messages:
            print(f"👤 You: {msg}")
            await chat_system.send_message(session_id, msg)
            
            # Wait for supplier response
            await asyncio.sleep(1)
            
            # Get latest messages
            chat_data = await chat_system.get_negotiation_chat(session_id)
            latest_supplier_msg = None
            
            for message in reversed(chat_data["messages"]):
                if message["sender_type"] == "supplier":
                    latest_supplier_msg = message
                    break
            
            if latest_supplier_msg:
                print(f"🏢 {latest_supplier_msg['sender']}: {latest_supplier_msg['content']}")
            
            print()
            
            # Check if negotiation concluded
            if not chat_data["is_active"]:
                break
            
            await asyncio.sleep(0.5)  # Pause between messages
        
        # Show final status
        final_chat = await chat_system.get_negotiation_chat(session_id)
        if final_chat["current_offer"]:
            savings = scenario["initial_price"] - final_chat["current_offer"]
            print(f"💰 Final Result: ₹{final_chat['current_offer']:.2f} (Saved: ₹{savings:.2f})")
        else:
            print("❌ Negotiation ended without agreement")
        
        print("─" * 50)
        print()
    
    # Show summary
    print("📊 Negotiation Summary:")
    summary = await chat_system.get_negotiation_summary()
    print(f"   Total Negotiations: {summary['total_negotiations']}")
    print(f"   Successful: {summary['successful_negotiations']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Total Savings: ₹{summary['total_savings']:.2f}")
    print(f"   Average Savings: ₹{summary['average_savings_per_negotiation']:.2f}")
    print()
    
    # Show active negotiations
    print("🔄 Active Negotiations:")
    active = await chat_system.get_active_negotiations()
    for session in active:
        print(f"   • {session['item_name']} with {session['supplier_name']}")
        print(f"     Phase: {session['phase']}, Messages: {session['message_count']}")
        if session['current_offer']:
            print(f"     Current offer: ₹{session['current_offer']:.2f}")
    
    if not active:
        print("   No active negotiations")
    
    print()
    print("✅ Demo completed! The negotiation system is ready for production use.")

async def demo_api_usage():
    """Demonstrate API usage patterns."""
    
    print("\n🔧 API Usage Examples:")
    print("=" * 40)
    
    # Show API endpoints
    endpoints = [
        {
            "method": "POST",
            "path": "/api/negotiations/start",
            "description": "Start new negotiation",
            "example": {
                "item_sku": "PEN001",
                "item_name": "Premium Pens",
                "initial_price": 450.00,
                "target_price": 380.00,
                "supplier_id": "rajesh_stationery",
                "quantity": 100
            }
        },
        {
            "method": "POST", 
            "path": "/api/negotiations/{session_id}/send",
            "description": "Send message in negotiation",
            "example": {
                "message": "Can you do ₹380 per unit for 100 pieces?"
            }
        },
        {
            "method": "GET",
            "path": "/api/negotiations/active",
            "description": "Get active negotiations",
            "example": "Returns list of active negotiations"
        },
        {
            "method": "GET",
            "path": "/api/negotiations/{session_id}/chat", 
            "description": "Get chat history",
            "example": "Returns complete conversation"
        },
        {
            "method": "GET",
            "path": "/api/negotiations/summary",
            "description": "Get negotiation statistics",
            "example": "Returns success rates and savings"
        }
    ]
    
    for endpoint in endpoints:
        print(f"{endpoint['method']} {endpoint['path']}")
        print(f"   {endpoint['description']}")
        if isinstance(endpoint['example'], dict):
            print(f"   Example: {json.dumps(endpoint['example'], indent=2)}")
        else:
            print(f"   {endpoint['example']}")
        print()

def print_ui_integration_guide():
    """Show how to integrate with UI dashboard."""
    
    print("🎨 UI Dashboard Integration Guide:")
    print("=" * 50)
    
    ui_components = [
        {
            "component": "NegotiationDashboard",
            "description": "Main negotiation management interface",
            "features": [
                "Active negotiations list",
                "Start new negotiation form", 
                "Real-time chat interface",
                "Savings analytics"
            ]
        },
        {
            "component": "ChatWindow",
            "description": "Real-time negotiation chat",
            "features": [
                "Message history display",
                "Send message input",
                "Typing indicators",
                "Price highlighting"
            ]
        },
        {
            "component": "SupplierCard",
            "description": "Supplier information display",
            "features": [
                "Company details",
                "Personality traits",
                "Response time estimates",
                "Success rate history"
            ]
        },
        {
            "component": "NegotiationMetrics",
            "description": "Analytics and KPIs",
            "features": [
                "Success rate charts",
                "Savings trends",
                "Active negotiations count",
                "Average negotiation time"
            ]
        }
    ]
    
    for component in ui_components:
        print(f"📱 {component['component']}")
        print(f"   {component['description']}")
        for feature in component['features']:
            print(f"   • {feature}")
        print()
    
    print("🔗 Integration Steps:")
    steps = [
        "Install required packages: axios, socket.io-client",
        "Create negotiation service for API calls",
        "Implement real-time updates with WebSocket",
        "Add price extraction and highlighting",
        "Create responsive chat UI components",
        "Integrate with main dashboard navigation"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    
    print("\n💡 Key Features to Highlight in UI:")
    features = [
        "🤖 AI-powered supplier responses",
        "💰 Real-time savings calculations", 
        "📊 Negotiation success analytics",
        "⚡ Instant message delivery",
        "🎯 Smart price suggestions",
        "📱 Mobile-responsive design"
    ]
    
    for feature in features:
        print(f"   {feature}")

async def main():
    """Run the complete demo."""
    print("🚀 VeriChain Negotiation System Complete Demo")
    print("=" * 60)
    print()
    
    # Run negotiation demo
    await demo_negotiation_system()
    
    # Show API usage
    await demo_api_usage()
    
    # Show UI integration guide
    print_ui_integration_guide()
    
    print("\n🎯 Next Steps:")
    next_steps = [
        "Start the FastAPI server: python scripts/start_server.py",
        "Test API endpoints at http://localhost:8000/docs",
        "Start sample negotiation: POST /api/negotiations/demo/start-sample",
        "Integrate with frontend dashboard",
        "Configure email notifications",
        "Set up production supplier contacts"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n📅 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())