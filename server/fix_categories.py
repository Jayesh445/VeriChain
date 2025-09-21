import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def fix_categories():
    async with AsyncSessionLocal() as db:
        # Update categories to match enum values
        await db.execute(text('UPDATE stationery_items SET category = "PAPER" WHERE category = "paper"'))
        await db.execute(text('UPDATE stationery_items SET category = "WRITING" WHERE category = "writing"'))
        await db.execute(text('UPDATE stationery_items SET category = "OFFICE_SUPPLIES" WHERE category = "office_supplies"'))
        await db.execute(text('UPDATE stationery_items SET category = "FILING" WHERE category = "filing"'))
        await db.commit()
        print('Updated all category values to match enum')

asyncio.run(fix_categories())