import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db
from app.core.logging import logger


async def main():
    """Initialize the database"""
    logger.info("Initializing database...")
    
    try:
        await init_db()
        logger.info("Database initialization completed successfully!")
        print("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())