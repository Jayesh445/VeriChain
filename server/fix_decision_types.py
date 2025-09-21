import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def fix_decision_types():
    async with AsyncSessionLocal() as db:
        await db.execute(text('UPDATE agent_decisions SET decision_type = "ALERT" WHERE decision_type = "alert"'))
        await db.execute(text('UPDATE agent_decisions SET decision_type = "REORDER" WHERE decision_type = "reorder"'))
        await db.execute(text('UPDATE agent_decisions SET decision_type = "VENDOR_RISK" WHERE decision_type = "vendor_risk"'))
        await db.execute(text('UPDATE agent_decisions SET decision_type = "ANOMALY" WHERE decision_type = "anomaly"'))
        await db.commit()
        print('Updated all decision types to match enum')

asyncio.run(fix_decision_types())