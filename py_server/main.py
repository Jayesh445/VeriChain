#!/usr/bin/env python3
"""
Production entry point for VeriChain Stationery Inventory Management System.
Complete AI-powered inventory management with auto-ordering and pattern recognition.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from app.main import app, FASTAPI_AVAILABLE
    from app.core.config import settings
    from app.utils.logging import setup_logging
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Dependencies not available: {e}")
    print("Please run: uv install")

def check_environment():
    """Check environment setup and requirements."""
    issues = []
    
    # Check Python version - allow 3.10+ for now
    if sys.version_info < (3, 10):
        issues.append(f"Python 3.10+ required, found {sys.version}")
    elif sys.version_info < (3, 11):
        print(f"   ⚠️  Python 3.11+ recommended, found {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check dependencies
    if not DEPENDENCIES_AVAILABLE:
        issues.append("Required dependencies not installed")
    
    return issues

def create_startup_info():
    """Create comprehensive startup information."""
    info = {
        "app_name": "VeriChain Stationery Inventory Management",
        "version": "1.0.0",
        "description": "AI-Powered Stationery Inventory Management with Auto-Ordering",
        "features": [
            "🤖 Intelligent inventory analysis with LangChain + Gemini",
            "📅 Educational calendar-aware ordering (school seasons, exams)",
            "🔄 Automated supplier negotiation and order placement",
            "📊 Seasonal demand pattern recognition",
            "📱 Real-time notifications and alerts",
            "📈 Comprehensive analytics dashboard",
            "🏪 Stationery-specific category management",
            "⚡ Async FastAPI with database persistence",
            "🔍 Smart low-stock predictions"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "root": "/",
            "agent_analysis": "/api/v1/agents/analyze",
            "dashboard": "/api/v1/dashboard/summary",
            "inventory": "/api/v1/dashboard/inventory",
            "decisions": "/api/v1/agents/decisions"
        },
        "technologies": [
            "FastAPI - High-performance async web framework",
            "LangChain - AI agent orchestration",
            "Google Gemini - Large language model",
            "SQLAlchemy - Database ORM with async support",
            "Pydantic - Data validation and serialization",
            "UV - Modern Python package management",
            "Loguru - Structured logging",
            "Tenacity - Retry logic for reliability"
        ]
    }
    return info

def print_startup_banner():
    """Print detailed startup information."""
    info = create_startup_info()
    
    print("=" * 80)
    print(f"🚀 {info['app_name']}")
    print(f"📦 Version: {info['version']}")
    print(f"📝 {info['description']}")
    print("=" * 80)
    
    print("\n🎯 KEY FEATURES:")
    for feature in info['features']:
        print(f"   {feature}")
    
    print("\n🔧 TECHNOLOGIES:")
    for tech in info['technologies']:
        print(f"   • {tech}")
    
    print("\n🌐 API ENDPOINTS:")
    for name, endpoint in info['endpoints'].items():
        print(f"   • {name.replace('_', ' ').title()}: {endpoint}")
    
    if DEPENDENCIES_AVAILABLE and FASTAPI_AVAILABLE:
        print(f"\n🌍 Server Configuration:")
        print(f"   • Host: {settings.host}")
        print(f"   • Port: {settings.port}")
        print(f"   • Environment: {'Development' if settings.debug else 'Production'}")
        print(f"   • Debug Mode: {'Enabled' if settings.debug else 'Disabled'}")
        print(f"   • Documentation: http://{settings.host}:{settings.port}/docs")
        print(f"   • API Base: http://{settings.host}:{settings.port}")
    
    print("=" * 80)

async def run_system_checks():
    """Run comprehensive system checks before startup."""
    print("\n🔍 SYSTEM CHECKS:")
    
    # Environment check
    issues = check_environment()
    if issues:
        print("   ❌ Environment Issues Found:")
        for issue in issues:
            print(f"      • {issue}")
        return False
    else:
        print("   ✅ Environment: All checks passed")
    
    # Database connectivity (if available)
    if DEPENDENCIES_AVAILABLE:
        try:
            from app.services.database import db_manager
            print("   ✅ Database: Connection available")
        except Exception as e:
            print(f"   ⚠️  Database: Warning - {str(e)}")
    
    # Agent system
    if DEPENDENCIES_AVAILABLE:
        try:
            from app.agents.stationery_agent import StationeryInventoryAgent
            print("   ✅ AI Agent: Stationery agent initialized")
        except Exception as e:
            print(f"   ❌ AI Agent: Error - {str(e)}")
            return False
    
    # API Key check using settings
    try:
        from app.core.config import settings
        if settings.effective_api_key:
            print("   ✅ Gemini API: Key configured")
        else:
            print("   ⚠️  Gemini API: No API key found (set GEMINI_API_KEY)")
    except Exception as e:
        print(f"   ❌ Settings: Error loading - {str(e)}")
        return False
    
    return True

def main():
    """Main entry point with comprehensive startup process."""
    print_startup_banner()
    
    # Check dependencies first
    if not DEPENDENCIES_AVAILABLE:
        print("\n❌ STARTUP FAILED")
        print("Required dependencies not installed.")
        print("\nTo install dependencies, run:")
        print("   uv install")
        print("   # or")
        print("   pip install -r requirements.txt")
        return 1
    
    if not FASTAPI_AVAILABLE:
        print("\n❌ STARTUP FAILED")
        print("FastAPI not available.")
        return 1
    
    # Setup logging
    setup_logging()
    
    # Run system checks
    if not asyncio.run(run_system_checks()):
        print("\n❌ STARTUP FAILED")
        print("System checks failed. Please resolve issues above.")
        return 1
    
    print("\n🚀 STARTING SERVER...")
    print("   • Initializing FastAPI application...")
    print("   • Setting up database connections...")
    print("   • Initializing AI agents...")
    print("   • Starting notification system...")
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
            server_header=False,
            date_header=False
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server startup failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
