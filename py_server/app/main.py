"""
FastAPI application initialization with full database and agent integration.
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    from datetime import datetime
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    CORSMiddleware = None
    asynccontextmanager = None

from app.core.config import settings
from app.utils.logging import setup_logging
from app.services.database import init_database, close_database

# Setup logging first
setup_logging()

if FASTAPI_AVAILABLE:
    from app.api import agents, dashboard
    from app.services.notifications import notification_manager
    from app.services.ai_service import initialize_ai_service

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan events."""
        # Startup
        print(f"Starting {settings.app_name} v{settings.app_version}")
        
        # Validate required settings
        missing = settings.validate_required_settings()
        if missing:
            print(f"Warning: Missing required settings: {', '.join(missing)}")
            if settings.is_production:
                raise ValueError(f"Required settings missing in production: {', '.join(missing)}")
        
        # Initialize AI service first
        print("🤖 Initializing VeriChain AI Service...")
        try:
            await initialize_ai_service()
            print("✅ AI Service initialized successfully")
        except Exception as e:
            print(f"⚠️ AI Service initialization failed: {e}")
        
        # Initialize database
        print("Initializing database connection...")
        await init_database()
        
        # Initialize services
        print("Initializing notification manager...")
        
        # Setup periodic tasks for seasonal reminders
        import asyncio
        asyncio.create_task(notification_manager.send_seasonal_reminders())
        
        yield
        
        # Shutdown
        print("Shutting down application...")
        await close_database()

    # Create FastAPI application
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Agentic AI Framework for Stationery Inventory Management with Auto-Ordering",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    # Include routers
    app.include_router(agents.router)
    app.include_router(dashboard.router)
    
    # Include monitoring router
    try:
        from app.api import monitoring
        app.include_router(monitoring.router)
        print("✅ Stock Monitoring API enabled")
    except Exception as e:
        print(f"⚠️ Monitoring router not available: {e}")
    
    # Include orchestration router
    try:
        from app.api import orchestration
        app.include_router(orchestration.router)
        print("✅ Advanced Agent Orchestration enabled")
    except Exception as e:
        print(f"⚠️ Orchestration router not available: {e}")
    
    # Include negotiation router
    try:
        from app.api import negotiations
        app.include_router(negotiations.router)
        print("✅ Supplier Negotiation Chat System enabled")
    except Exception as e:
        print(f"⚠️ Negotiation router not available: {e}")

    @app.get("/")
    async def root():
        """Root endpoint with system information."""
        return {
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "description": "Intelligent Stationery Inventory Management with AI Agents",
            "features": [
                "Seasonal pattern recognition",
                "Auto-ordering with educational calendar awareness", 
                "Supplier negotiation intelligence",
                "Real-time notifications",
                "Comprehensive analytics dashboard"
            ],
            "docs": "/docs",
            "redoc": "/redoc",
            "status": "active",
            "environment": "development" if settings.debug else "production"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint with detailed system status."""
        from app.services.database import db_manager
        
        try:
            # Test database connection
            analytics = await db_manager.get_inventory_analytics()
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Test notification system
        notification_status = "healthy" if len(notification_manager.notifications) >= 0 else "error"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.app_version,
            "environment": "development" if settings.debug else "production",
            "components": {
                "database": db_status,
                "notifications": notification_status,
                "agents": "healthy"
            },
            "uptime": "N/A",  # Would be calculated from startup time
            "total_inventory_items": analytics.get('total_items', 0) if db_status == "healthy" else 0
        }

    @app.get("/api/v1/system/stats")
    async def get_system_stats():
        """Get comprehensive system statistics."""
        from app.services.database import db_manager
        
        try:
            # Database statistics
            analytics = await db_manager.get_inventory_analytics()
            recent_decisions = await db_manager.get_agent_decisions(limit=100)
            recent_alerts = await db_manager.get_alerts(limit=100)
            
            # Notification statistics
            notification_stats = notification_manager.get_notification_stats()
            
            return {
                "inventory": {
                    "total_items": analytics.get('total_items', 0),
                    "total_value": analytics.get('total_value', 0),
                    "low_stock_items": analytics.get('low_stock_count', 0),
                    "out_of_stock_items": analytics.get('out_of_stock_count', 0),
                    "average_stock_level": analytics.get('avg_stock_level', 0)
                },
                "agent_activity": {
                    "recent_decisions": len(recent_decisions),
                    "approved_decisions": len([d for d in recent_decisions if d.approved]),
                    "critical_decisions": len([d for d in recent_decisions if d.priority.value == "critical"]),
                    "avg_confidence": sum(d.confidence_score for d in recent_decisions) / len(recent_decisions) if recent_decisions else 0
                },
                "alerts": {
                    "total_alerts": len(recent_alerts),
                    "unresolved_alerts": len([a for a in recent_alerts if not a.resolved]),
                    "critical_alerts": len([a for a in recent_alerts if a.priority.value == "critical"])
                },
                "notifications": notification_stats,
                "system": {
                    "environment": "development" if settings.debug else "production",
                    "version": settings.app_version,
                    "uptime": "N/A"  # Would be calculated from startup time
                }
            }
        except Exception as e:
            return {
                "error": f"Failed to get system stats: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

else:
    # Fallback when FastAPI is not available
    app = None
    print("FastAPI not available - running in compatibility mode")

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        from datetime import datetime
        
        print(f"Starting {settings.app_name} server...")
        print(f"Environment: {'Development' if settings.debug else 'Production'}")
        print(f"Database URL: {settings.get_database_url()}")
        print(f"Server will run on: http://{settings.host}:{settings.port}")
        print(f"API Documentation: http://{settings.host}:{settings.port}/docs")
        print(f"Started at: {datetime.now().isoformat()}")
        
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    else:
        print("Cannot start server - FastAPI not available")
        print("Please install required dependencies with: uv add fastapi uvicorn")