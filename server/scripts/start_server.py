import uvicorn
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting VeriChain Agentic Supply Chain Server...")
    print(f"📡 Server will run on http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API documentation available at http://{settings.api_host}:{settings.api_port}/docs")
    print("="*60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )