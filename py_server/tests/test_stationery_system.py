"""
Test suite for stationery inventory management system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from app.models import (
    InventoryItem, SalesData, SupplierInfo, AgentDecision,
    Priority, ActionType, InventoryStatus, AgentRole
)
from app.agents.stationery_agent import (
    StationeryInventoryAgent, StationeryCategory, 
    StationeryPatternDatabase, create_stationery_agent
)
from app.services.pattern_analysis import create_pattern_analyzer
from app.services.notifications import notification_manager, NotificationTemplate


class TestStationeryInventoryAgent:
    """Test cases for stationery inventory agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return create_stationery_agent()
    
    @pytest.fixture
    def sample_stationery_items(self) -> List[InventoryItem]:
        """Create sample stationery inventory items."""
        return [
            InventoryItem(
                sku="PEN001",
                name="Blue Ballpoint Pen",
                category="writing_instruments",
                current_stock=50,
                min_stock_threshold=100,
                max_stock_capacity=500,
                unit_cost=2.50,
                supplier_id="SUPPLIER001",
                lead_time_days=7
            ),
            InventoryItem(
                sku="NOTEBOOK001",
                name="A4 Ruled Notebook",
                category="paper_products",
                current_stock=25,
                min_stock_threshold=50,
                max_stock_capacity=200,
                unit_cost=5.00,
                supplier_id="SUPPLIER002",
                lead_time_days=10
            ),
            InventoryItem(
                sku="TEXTBOOK001",
                name="Mathematics Grade 10",
                category="educational_books",
                current_stock=10,
                min_stock_threshold=30,
                max_stock_capacity=100,
                unit_cost=25.00,
                supplier_id="SUPPLIER003",
                lead_time_days=14
            ),
            InventoryItem(
                sku="CALCULATOR001",
                name="Scientific Calculator",
                category="calculators",
                current_stock=5,
                min_stock_threshold=20,
                max_stock_capacity=50,
                unit_cost=15.00,
                supplier_id="SUPPLIER001",
                lead_time_days=5
            )
        ]
    
    @pytest.fixture
    def sample_sales_data(self) -> List[SalesData]:
        """Create sample sales data with seasonal patterns."""
        sales_data = []
        base_date = datetime.now() - timedelta(days=365)
        
        # Simulate seasonal sales patterns
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            month = current_date.month
            
            # School opening season (June-July) - higher sales
            if month in [6, 7]:
                multiplier = 3.0
            # Exam seasons (November, March) - medium sales
            elif month in [11, 3]:
                multiplier = 2.0
            # Regular periods
            else:
                multiplier = 1.0
            
            # Add sales for different items
            sales_data.extend([
                SalesData(
                    sku="PEN001",
                    date=current_date,
                    quantity_sold=int(10 * multiplier),
                    revenue=25.0 * multiplier,
                    channel="retail"
                ),
                SalesData(
                    sku="NOTEBOOK001",
                    date=current_date,
                    quantity_sold=int(5 * multiplier),
                    revenue=25.0 * multiplier,
                    channel="online"
                ),
                SalesData(
                    sku="TEXTBOOK001",
                    date=current_date,
                    quantity_sold=int(2 * multiplier) if month in [4, 5, 6] else 1,
                    revenue=50.0 * multiplier if month in [4, 5, 6] else 25.0,
                    channel="retail"
                )
            ])
        
        return sales_data
    
    @pytest.fixture
    def sample_suppliers(self) -> List[SupplierInfo]:
        """Create sample supplier information."""
        return [
            SupplierInfo(
                name="Office Supplies Co.",
                contact_email="orders@officesupplies.com",
                reliability_score=8.5,
                average_lead_time=7,
                min_order_quantity=50
            ),
            SupplierInfo(
                name="Educational Materials Ltd.",
                contact_email="sales@edumat.com",
                reliability_score=9.2,
                average_lead_time=10,
                min_order_quantity=25
            ),
            SupplierInfo(
                name="Stationery World",
                contact_email="bulk@stationeryworld.com",
                reliability_score=7.8,
                average_lead_time=5,
                min_order_quantity=100
            )
        ]
    
    def test_categorize_stationery_item(self, agent):
        """Test stationery item categorization."""
        pen = InventoryItem(sku="TEST001", name="Blue Pen", category="test")
        assert agent.categorize_stationery_item(pen) == StationeryCategory.WRITING_INSTRUMENTS
        
        notebook = InventoryItem(sku="TEST002", name="A4 Notebook", category="test")
        assert agent.categorize_stationery_item(notebook) == StationeryCategory.PAPER_PRODUCTS
        
        textbook = InventoryItem(sku="TEST003", name="Math Textbook", category="test")
        assert agent.categorize_stationery_item(textbook) == StationeryCategory.EDUCATIONAL_BOOKS
        
        calculator = InventoryItem(sku="TEST004", name="Scientific Calculator", category="test")
        assert agent.categorize_stationery_item(calculator) == StationeryCategory.CALCULATORS
    
    def test_seasonal_demand_analysis(self, agent, sample_stationery_items, sample_sales_data):
        """Test seasonal demand analysis."""
        pen_item = sample_stationery_items[0]  # Blue Ballpoint Pen
        current_month = 6  # June - school opening season
        
        analysis = agent.analyze_seasonal_demand(pen_item, sample_sales_data, current_month)
        
        assert analysis["category"] == "writing_instruments"
        assert analysis["is_peak_season"] == True
        assert analysis["current_multiplier"] == 2.5  # Expected multiplier for writing instruments in June
        assert "predictions" in analysis
        assert len(analysis["predictions"]) == 3  # Next 3 months
    
    def test_optimal_order_quantity_calculation(self, agent, sample_stationery_items, sample_sales_data, sample_suppliers):
        """Test optimal order quantity calculation."""
        pen_item = sample_stationery_items[0]
        supplier = sample_suppliers[0]
        
        # Simulate demand analysis
        demand_analysis = agent.analyze_seasonal_demand(pen_item, sample_sales_data, 6)
        
        order_quantity, reasoning = agent.calculate_optimal_order_quantity(
            pen_item, demand_analysis, supplier
        )
        
        assert order_quantity > 0
        assert isinstance(reasoning, str)
        assert len(reasoning) > 10
        
        # Test with supplier minimum order quantity
        assert order_quantity >= supplier.min_order_quantity
    
    def test_urgency_assessment(self, agent, sample_stationery_items, sample_sales_data):
        """Test urgency assessment based on stock levels and patterns."""
        # Test critical stock (out of stock)
        critical_item = sample_stationery_items[0]
        critical_item.current_stock = 0
        demand_analysis = agent.analyze_seasonal_demand(critical_item, sample_sales_data, 6)
        
        priority = agent.assess_urgency(critical_item, demand_analysis)
        assert priority == Priority.CRITICAL
        
        # Test low stock during peak season
        low_stock_item = sample_stationery_items[1]
        low_stock_item.current_stock = 10
        demand_analysis = agent.analyze_seasonal_demand(low_stock_item, sample_sales_data, 6)
        
        priority = agent.assess_urgency(low_stock_item, demand_analysis)
        assert priority in [Priority.HIGH, Priority.CRITICAL]
    
    def test_auto_order_decision_creation(self, agent, sample_stationery_items, sample_sales_data, sample_suppliers):
        """Test automated order decision creation."""
        item = sample_stationery_items[0]
        supplier = sample_suppliers[0]
        
        decision = agent.create_auto_order_decision(item, sample_sales_data, supplier)
        
        assert isinstance(decision, AgentDecision)
        assert decision.agent_role == AgentRole.SUPPLY_CHAIN_MANAGER
        assert decision.item_sku == item.sku
        assert decision.action_type in [ActionType.RESTOCK, ActionType.HOLD]
        assert decision.priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]
        assert 0 <= decision.confidence_score <= 1
        assert len(decision.reasoning) > 20
        
        if decision.recommended_quantity:
            assert decision.recommended_quantity > 0
            assert decision.estimated_cost > 0
    
    def test_portfolio_analysis(self, agent, sample_stationery_items, sample_sales_data, sample_suppliers):
        """Test comprehensive portfolio analysis."""
        decisions = agent.analyze_stationery_portfolio(
            sample_stationery_items, sample_sales_data, sample_suppliers
        )
        
        assert len(decisions) == len(sample_stationery_items)
        assert all(isinstance(d, AgentDecision) for d in decisions)
        
        # Check that decisions are sorted by priority
        priorities = [d.priority.value for d in decisions]
        priority_values = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        priority_scores = [priority_values[p] for p in priorities]
        
        # Should be sorted in descending order (highest priority first)
        assert priority_scores == sorted(priority_scores, reverse=True)
    
    def test_negotiation_strategy_generation(self, agent, sample_stationery_items, sample_suppliers):
        """Test supplier negotiation strategy generation."""
        strategy = agent.generate_negotiation_strategy(sample_stationery_items, sample_suppliers[0])
        
        assert "total_order_value" in strategy
        assert "category_breakdown" in strategy
        assert "negotiation_points" in strategy
        assert "recommended_discount_target" in strategy
        assert "payment_terms" in strategy
        
        assert strategy["total_order_value"] > 0
        assert len(strategy["negotiation_points"]) > 0
        assert 5 <= strategy["recommended_discount_target"] <= 15
    
    def test_dashboard_insights(self, agent, sample_stationery_items, sample_sales_data):
        """Test dashboard insights generation."""
        insights = agent.get_dashboard_insights(sample_stationery_items, sample_sales_data)
        
        assert "total_inventory_value" in insights
        assert "category_breakdown" in insights
        assert "critical_items_count" in insights
        assert "seasonal_opportunities" in insights
        assert "calendar_insights" in insights
        assert "health_score" in insights
        assert "next_peak_season" in insights
        
        assert insights["total_inventory_value"] > 0
        assert 0 <= insights["health_score"] <= 100


class TestPatternAnalysis:
    """Test cases for pattern analysis service."""
    
    @pytest.fixture
    def analyzer(self):
        """Create pattern analyzer instance."""
        return create_pattern_analyzer()
    
    def test_seasonal_pattern_detection(self, analyzer):
        """Test seasonal pattern detection."""
        # Create sample data with clear seasonal pattern
        sales_data = []
        item = InventoryItem(sku="TEST001", name="Test Pen", category="writing_instruments")
        
        base_date = datetime.now() - timedelta(days=365)
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            month = current_date.month
            
            # Higher sales in June (school opening)
            quantity = 30 if month == 6 else 10
            
            sales_data.append(SalesData(
                sku="TEST001",
                date=current_date,
                quantity_sold=quantity,
                revenue=quantity * 2.5
            ))
        
        insights = analyzer.analyze_seasonal_patterns(sales_data, item)
        
        # Should detect June as a seasonal spike
        june_insights = [i for i in insights if "June" in i.description]
        assert len(june_insights) > 0
        
        june_insight = june_insights[0]
        assert june_insight.insight_type == "seasonal_spike"
        assert june_insight.confidence > 0.6
    
    def test_trend_analysis(self, analyzer):
        """Test trend pattern analysis."""
        # Create data with growth trend
        sales_data = []
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(180):
            current_date = base_date + timedelta(days=i)
            # Simulate growth trend
            quantity = 10 + (i // 30)  # Gradual increase
            
            sales_data.append(SalesData(
                sku="TEST001",
                date=current_date,
                quantity_sold=quantity,
                revenue=quantity * 2.5
            ))
        
        insights = analyzer.analyze_trend_patterns(sales_data)
        
        # Should detect growth trend
        growth_insights = [i for i in insights if i.insight_type == "growth_trend"]
        assert len(growth_insights) > 0
        
        growth_insight = growth_insights[0]
        assert growth_insight.confidence > 0.7
        assert "growth" in growth_insight.description.lower()
    
    def test_anomaly_detection(self, analyzer):
        """Test anomaly detection."""
        # Create data with clear anomaly
        sales_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            # Normal sales except one anomaly
            quantity = 100 if i == 15 else 10  # Big spike on day 15
            
            sales_data.append(SalesData(
                sku="TEST001",
                date=current_date,
                quantity_sold=quantity,
                revenue=quantity * 2.5
            ))
        
        insights = analyzer.detect_anomalies(sales_data)
        
        # Should detect the anomaly
        anomaly_insights = [i for i in insights if i.insight_type == "demand_anomaly"]
        assert len(anomaly_insights) > 0
        
        anomaly_insight = anomaly_insights[0]
        assert anomaly_insight.confidence > 0.8
        assert "100 units" in anomaly_insight.description


class TestNotificationSystem:
    """Test cases for notification system."""
    
    def test_order_alert_creation(self):
        """Test order alert notification creation."""
        decision = AgentDecision(
            agent_role=AgentRole.SUPPLY_CHAIN_MANAGER,
            item_sku="TEST001",
            action_type=ActionType.RESTOCK,
            priority=Priority.HIGH,
            confidence_score=0.85,
            reasoning="Test reasoning",
            recommended_quantity=100,
            estimated_cost=250.0
        )
        
        notification = NotificationTemplate.create_order_alert(decision)
        
        assert notification.type.value == "order_alert"
        assert notification.priority == Priority.HIGH
        assert "TEST001" in notification.title
        assert "100 units" in notification.message
        assert "$250.00" in notification.message
        assert notification.data["decision_id"] == str(decision.id)
    
    def test_stock_warning_creation(self):
        """Test stock warning notification creation."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            category="test",
            current_stock=5,
            min_stock_threshold=20,
            max_stock_capacity=100,
            unit_cost=2.50
        )
        
        notification = NotificationTemplate.create_stock_warning(item)
        
        assert notification.type.value == "stock_warning"
        assert notification.priority == Priority.HIGH
        assert "LOW STOCK" in notification.title
        assert "TEST001" in notification.message
        assert notification.data["current_stock"] == 5
        assert notification.data["min_threshold"] == 20
    
    @pytest.mark.asyncio
    async def test_notification_manager(self):
        """Test notification manager functionality."""
        # Clear any existing notifications
        notification_manager.notifications.clear()
        
        decision = AgentDecision(
            agent_role=AgentRole.SUPPLY_CHAIN_MANAGER,
            item_sku="TEST001",
            action_type=ActionType.RESTOCK,
            priority=Priority.CRITICAL,
            confidence_score=0.9,
            reasoning="Critical restock needed"
        )
        
        # Process critical decisions
        await notification_manager.process_decisions([decision])
        
        # Should have created a notification
        assert len(notification_manager.notifications) > 0
        
        # Get recent notifications
        recent = notification_manager.get_recent_notifications(10)
        assert len(recent) > 0
        
        # Test unread notifications
        unread = notification_manager.get_unread_notifications()
        assert len(unread) > 0
        
        # Mark as read
        notification_id = notification_manager.notifications[0].id
        notification_manager.mark_as_read(notification_id)
        
        # Should have fewer unread notifications
        unread_after = notification_manager.get_unread_notifications()
        assert len(unread_after) == len(unread) - 1


class TestEducationalCalendar:
    """Test educational calendar awareness."""
    
    def test_seasonal_event_detection(self):
        """Test detection of educational calendar events."""
        from app.services.pattern_analysis import EducationalCalendarAnalyzer
        
        # Test school opening season
        assert EducationalCalendarAnalyzer.get_event_for_month(6) == "school_opening"
        assert EducationalCalendarAnalyzer.get_event_for_month(7) == "school_opening"
        
        # Test exam preparation
        assert EducationalCalendarAnalyzer.get_event_for_month(11) == "exam_preparation"
        assert EducationalCalendarAnalyzer.get_event_for_month(3) == "exam_preparation"
        
        # Test impact factors
        assert EducationalCalendarAnalyzer.get_impact_factor(6) == 3.0  # High impact
        assert EducationalCalendarAnalyzer.get_impact_factor(12) == 0.7  # Holiday season
    
    def test_seasonal_pattern_database(self):
        """Test seasonal pattern database."""
        # Test writing instruments pattern
        pattern = StationeryPatternDatabase.get_pattern(StationeryCategory.WRITING_INSTRUMENTS)
        assert 6 in pattern.peak_months  # June is peak for writing instruments
        assert 7 in pattern.peak_months  # July is peak for writing instruments
        assert pattern.multiplier > 1.0
        
        # Test educational books pattern
        edu_pattern = StationeryPatternDatabase.get_pattern(StationeryCategory.EDUCATIONAL_BOOKS)
        assert 4 in edu_pattern.peak_months  # April preparation
        assert 5 in edu_pattern.peak_months  # May preparation
        assert 6 in edu_pattern.peak_months  # June school opening
        assert edu_pattern.multiplier > 3.0  # High impact for books
        
        # Test peak season detection
        assert StationeryPatternDatabase.is_peak_season(StationeryCategory.WRITING_INSTRUMENTS, 6) == True
        assert StationeryPatternDatabase.is_peak_season(StationeryCategory.WRITING_INSTRUMENTS, 1) == False


# Integration Tests
class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow from inventory analysis to notifications."""
        # Create test data
        agent = create_stationery_agent()
        analyzer = create_pattern_analyzer()
        
        # Sample inventory
        items = [
            InventoryItem(
                sku="PEN001",
                name="Blue Pen",
                category="writing_instruments",
                current_stock=5,  # Low stock
                min_stock_threshold=50,
                max_stock_capacity=200,
                unit_cost=2.0,
                lead_time_days=7
            )
        ]
        
        # Sample sales data showing seasonal pattern
        sales_data = []
        base_date = datetime.now() - timedelta(days=90)
        for i in range(90):
            current_date = base_date + timedelta(days=i)
            quantity = 15 if current_date.month == 6 else 5  # Higher in June
            
            sales_data.append(SalesData(
                sku="PEN001",
                date=current_date,
                quantity_sold=quantity,
                revenue=quantity * 2.0
            ))
        
        # Run analysis
        decisions = agent.analyze_stationery_portfolio(items, sales_data)
        
        # Should generate decisions
        assert len(decisions) > 0
        decision = decisions[0]
        assert decision.item_sku == "PEN001"
        assert decision.action_type == ActionType.RESTOCK
        
        # Run pattern analysis
        comprehensive_analysis = analyzer.generate_comprehensive_analysis(sales_data, items)
        assert comprehensive_analysis["total_insights"] >= 0
        
        # Test notification generation
        await notification_manager.process_decisions(decisions)
        notifications = notification_manager.get_recent_notifications(5)
        
        # Should have notifications for critical decisions
        critical_decisions = [d for d in decisions if d.priority in [Priority.CRITICAL, Priority.HIGH]]
        if critical_decisions:
            assert len(notifications) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])