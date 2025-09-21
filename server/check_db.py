import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_tables():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print('Tables:', [table[0] for table in tables])
        
        result = await db.execute(text('SELECT COUNT(*) FROM stationery_items'))
        count = result.scalar()
        print(f'Items count: {count}')
        
        if count > 0:
            result = await db.execute(text('SELECT id, name, sku, current_stock FROM stationery_items LIMIT 3'))
            items = result.fetchall()
            print('Sample items:', items)

asyncio.run(check_tables())