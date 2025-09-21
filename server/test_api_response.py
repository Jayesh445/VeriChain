import asyncio
import json
from app.core.database import AsyncSessionLocal
from app.services.database import InventoryService

async def test_api_response():
    async with AsyncSessionLocal() as db:
        try:
            items = await InventoryService.get_all_items(db)
            print(f'Service returned {len(items)} items')
            
            # Try to convert to response format 
            for item in items[:2]:
                response_data = {
                    "id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "category": item.category.value if hasattr(item.category, 'value') else str(item.category),
                    "brand": item.brand,
                    "unit": item.unit,
                    "unit_cost": item.unit_cost,
                    "current_stock": item.current_stock,
                    "reorder_level": item.reorder_level,
                    "max_stock_level": item.max_stock_level,
                    "is_active": item.is_active,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                }
                print(f'Item response: {json.dumps(response_data, indent=2)}')
                
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

asyncio.run(test_api_response())