import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.services.database import InventoryService, SalesService
from app.agents.workflow_orchestrator import AgentWorkflowOrchestrator
from app.models import ItemCategory


class TestStationerySystem:
    """Basic tests for the stationery management system"""
    
    @pytest.fixture
    async def db_session(self):
        """Create a test database session"""
        await init_db()
        async with AsyncSessionLocal() as session:
            yield session
    
    @pytest.mark.asyncio
    async def test_inventory_service(self, db_session: AsyncSession):
        """Test basic inventory operations"""
        # This would normally use a test database
        summary = await InventoryService.get_inventory_summary(db_session)
        assert "total_items" in summary
        assert "low_stock_items" in summary
        assert "out_of_stock_items" in summary
    
    @pytest.mark.asyncio
    async def test_sales_service(self, db_session: AsyncSession):
        """Test sales operations"""
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        trends = await SalesService.get_sales_trends(db_session, days=7)
        assert isinstance(trends, list)
    
    @pytest.mark.asyncio
    async def test_workflow_orchestrator(self, db_session: AsyncSession):
        """Test the agent workflow orchestrator"""
        orchestrator = AgentWorkflowOrchestrator()
        
        # This would normally mock the AI calls
        assert orchestrator is not None
        assert hasattr(orchestrator, 'trigger_full_analysis')
    
    def test_item_categories(self):
        """Test item categories enum"""
        assert ItemCategory.WRITING == "writing"
        assert ItemCategory.PAPER == "paper"
        assert ItemCategory.OFFICE_SUPPLIES == "office_supplies"


if __name__ == "__main__":
    pytest.main([__file__])