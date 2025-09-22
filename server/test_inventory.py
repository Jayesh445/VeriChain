import asyncio
from app.core.database import AsyncSessionLocal
from app.services.database import InventoryService

async def test_inventory_service():
    async with AsyncSessionLocal() as db:
        try:
            items = await InventoryService.get_all_items(db)
            print(f'Found {len(items)} items')
            for item in items[:3]:
                print(f'Item: {item.id}, {item.name}, active: {item.is_active}')
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

asyncio.run(test_inventory_service())