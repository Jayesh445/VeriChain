"""
VeriChain AI-Powered Server Startup Script
Initializes all AI services and starts the FastAPI server.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.ai_service import initialize_ai_service
from app.services.database import init_database
from app.services.negotiation_chat import initialize_negotiation_chat
from app.services.auto_ordering import initialize_auto_ordering

async def initialize_all_services():
    """Initialize all VeriChain AI services."""
    print("🚀 VeriChain AI System Startup")
    print("=" * 50)
    
    # Check API key
    api_key = (
        settings.google_api_key or 
        settings.gemini_api_key or 
        os.getenv('GOOGLE_API_KEY') or 
        os.getenv('GEMINI_API_KEY')
    )
    
    if not api_key:
        print("❌ ERROR: No Google API key found!")
        print("💡 Please set one of these environment variables:")
        print("   - GOOGLE_API_KEY")
        print("   - GEMINI_API_KEY")
        print("\n📝 Example (PowerShell):")
        print("   $env:GOOGLE_API_KEY='your_api_key_here'")
        return False
    
    print(f"✅ API key detected: {api_key[:10]}...")
    
    try:
        # Initialize services in order
        print("\n🤖 Initializing AI Service...")
        await initialize_ai_service()
        print("✅ AI Service ready")
        
        print("\n🗄️ Initializing Database...")
        await init_database()
        print("✅ Database ready")
        
        print("\n💬 Initializing Negotiation System...")
        await initialize_negotiation_chat()
        print("✅ Negotiation System ready")
        
        print("\n📦 Initializing Auto-Ordering...")
        await initialize_auto_ordering()
        print("✅ Auto-Ordering ready")
        
        print("\n🎯 All services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    print("\n🌐 Starting FastAPI Server...")
    print(f"🔗 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📖 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Interactive API: http://{settings.host}:{settings.port}/redoc")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Install with: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

async def main():
    """Main startup function."""
    # Initialize all services
    if await initialize_all_services():
        print("\n✨ VeriChain AI System Ready!")
        print("🎮 You can now:")
        print("   • Run negotiations via API")
        print("   • Monitor auto-ordering decisions")
        print("   • Access AI inventory analytics")
        print("   • Test all endpoints")
        
        # Start the server
        start_server()
    else:
        print("\n❌ Startup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)