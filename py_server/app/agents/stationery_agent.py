"""
Comprehensive Stationery Inventory Management Agent with pattern recognition and auto-ordering.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, Field
from loguru import logger

from app.models import (
    InventoryItem, SalesData, SupplierInfo, AgentDecision, 
    ActionType, Priority, AgentRole
)


class StationeryCategory(str, Enum):
    """Stationery product categories with seasonal patterns."""
    WRITING_INSTRUMENTS = "writing_instruments"  # Pens, pencils, markers
    PAPER_PRODUCTS = "paper_products"  # Notebooks, sheets, graph paper
    EDUCATIONAL_BOOKS = "educational_books"  # Textbooks, workbooks
    ART_SUPPLIES = "art_supplies"  # Colors, brushes, drawing books
    OFFICE_SUPPLIES = "office_supplies"  # Staplers, clips, folders
    CALCULATORS = "calculators"  # Scientific, basic calculators
    SCHOOL_BAGS = "school_bags"  # Backpacks, lunch boxes
    GEOMETRY_TOOLS = "geometry_tools"  # Rulers, compass, protractor


class SeasonalEvent(str, Enum):
    """Educational calendar events affecting demand."""
    SCHOOL_OPENING = "school_opening"  # June-July
    MID_SESSION = "mid_session"  # September-November
    EXAM_PERIOD = "exam_period"  # November-December, March-April
    NEW_YEAR_SESSION = "new_year_session"  # January
    ADMISSION_SEASON = "admission_season"  # April-May


@dataclass
class SeasonalPattern:
    """Seasonal demand pattern for stationery items."""
    category: StationeryCategory
    peak_months: List[int]  # Months with highest demand (1-12)
    multiplier: float  # Demand multiplier during peak
    lead_time_adjustment: int  # Days to adjust lead time
    description: str


class StationeryPatternDatabase:
    """Database of stationery seasonal patterns and intelligence."""
    
    PATTERNS = {
        StationeryCategory.WRITING_INSTRUMENTS: SeasonalPattern(
            category=StationeryCategory.WRITING_INSTRUMENTS,
            peak_months=[6, 7, 11, 12],  # School opening + exam periods
            multiplier=2.5,
            lead_time_adjustment=-10,
            description="High demand during school opening and exam periods"
        ),
        StationeryCategory.PAPER_PRODUCTS: SeasonalPattern(
            category=StationeryCategory.PAPER_PRODUCTS,
            peak_months=[6, 7, 1],  # School opening + new session
            multiplier=3.0,
            lead_time_adjustment=-15,
            description="Maximum demand during school session starts"
        ),
        StationeryCategory.EDUCATIONAL_BOOKS: SeasonalPattern(
            category=StationeryCategory.EDUCATIONAL_BOOKS,
            peak_months=[4, 5, 6],  # Pre-school preparation period
            multiplier=4.0,
            lead_time_adjustment=-30,
            description="Critical for new academic year preparation"
        ),
        StationeryCategory.ART_SUPPLIES: SeasonalPattern(
            category=StationeryCategory.ART_SUPPLIES,
            peak_months=[6, 7, 9],  # School opening + art project seasons
            multiplier=2.0,
            lead_time_adjustment=-7,
            description="Steady with spikes during creative project periods"
        ),
        StationeryCategory.OFFICE_SUPPLIES: SeasonalPattern(
            category=StationeryCategory.OFFICE_SUPPLIES,
            peak_months=[1, 4, 7, 10],  # Quarterly cycles
            multiplier=1.5,
            lead_time_adjustment=0,
            description="Business quarterly restocking cycles"
        ),
        StationeryCategory.CALCULATORS: SeasonalPattern(
            category=StationeryCategory.CALCULATORS,
            peak_months=[6, 7],  # School opening
            multiplier=3.5,
            lead_time_adjustment=-20,
            description="Essential for new academic year, especially higher grades"
        ),
        StationeryCategory.SCHOOL_BAGS: SeasonalPattern(
            category=StationeryCategory.SCHOOL_BAGS,
            peak_months=[5, 6],  # Pre-school shopping
            multiplier=5.0,
            lead_time_adjustment=-45,
            description="Annual replacement before school year"
        ),
        StationeryCategory.GEOMETRY_TOOLS: SeasonalPattern(
            category=StationeryCategory.GEOMETRY_TOOLS,
            peak_months=[6, 7, 9],  # School opening + math-heavy periods
            multiplier=2.2,
            lead_time_adjustment=-10,
            description="Mathematics and technical drawing requirements"
        )
    }
    
    @classmethod
    def get_pattern(cls, category: StationeryCategory) -> SeasonalPattern:
        """Get seasonal pattern for a category."""
        return cls.PATTERNS.get(category, SeasonalPattern(
            category=category,
            peak_months=[6, 7],
            multiplier=1.5,
            lead_time_adjustment=0,
            description="Default pattern"
        ))
    
    @classmethod
    def is_peak_season(cls, category: StationeryCategory, month: int) -> bool:
        """Check if current month is peak season for category."""
        pattern = cls.get_pattern(category)
        return month in pattern.peak_months
    
    @classmethod
    def get_demand_multiplier(cls, category: StationeryCategory, month: int) -> float:
        """Get demand multiplier for category in given month."""
        pattern = cls.get_pattern(category)
        if month in pattern.peak_months:
            return pattern.multiplier
        return 1.0


class StationeryInventoryAgent:
    """
    Intelligent Stationery Inventory Management Agent with:
    - Seasonal pattern recognition
    - Auto-ordering with educational calendar awareness
    - Supplier negotiation intelligence
    - Demand forecasting for stationery items
    """
    
    def __init__(self):
        self.agent_role = AgentRole.SUPPLY_CHAIN_MANAGER
        self.pattern_db = StationeryPatternDatabase()
        logger.info("Initialized Stationery Inventory Agent")
    
    def categorize_stationery_item(self, item: InventoryItem) -> StationeryCategory:
        """Categorize stationery item based on name/description."""
        name_lower = item.name.lower()
        
        # Writing instruments
        if any(word in name_lower for word in ['pen', 'pencil', 'marker', 'highlighter', 'ink']):
            return StationeryCategory.WRITING_INSTRUMENTS
        
        # Paper products
        elif any(word in name_lower for word in ['notebook', 'paper', 'sheet', 'pad', 'diary']):
            return StationeryCategory.PAPER_PRODUCTS
        
        # Educational books
        elif any(word in name_lower for word in ['book', 'textbook', 'workbook', 'guide']):
            return StationeryCategory.EDUCATIONAL_BOOKS
        
        # Art supplies
        elif any(word in name_lower for word in ['color', 'paint', 'brush', 'crayon', 'drawing']):
            return StationeryCategory.ART_SUPPLIES
        
        # Calculators
        elif any(word in name_lower for word in ['calculator', 'scientific', 'graphing']):
            return StationeryCategory.CALCULATORS
        
        # School bags
        elif any(word in name_lower for word in ['bag', 'backpack', 'school bag', 'lunch']):
            return StationeryCategory.SCHOOL_BAGS
        
        # Geometry tools
        elif any(word in name_lower for word in ['ruler', 'compass', 'protractor', 'geometry', 'scale']):
            return StationeryCategory.GEOMETRY_TOOLS
        
        # Default to office supplies
        else:
            return StationeryCategory.OFFICE_SUPPLIES
    
    def analyze_seasonal_demand(
        self, 
        item: InventoryItem, 
        sales_data: List[SalesData],
        current_month: int
    ) -> Dict[str, Any]:
        """Analyze seasonal demand patterns for stationery item."""
        category = self.categorize_stationery_item(item)
        pattern = self.pattern_db.get_pattern(category)
        
        # Calculate historical monthly averages
        monthly_sales = {}
        for sale in sales_data:
            if sale.sku == item.sku:
                month = sale.date.month
                if month not in monthly_sales:
                    monthly_sales[month] = []
                monthly_sales[month].append(sale.quantity_sold)
        
        # Calculate average sales per month
        monthly_averages = {}
        for month, sales in monthly_sales.items():
            monthly_averages[month] = sum(sales) / len(sales)
        
        # Predict demand for next 3 months
        predictions = {}
        base_demand = sum(monthly_averages.values()) / len(monthly_averages) if monthly_averages else item.min_stock_threshold
        
        for i in range(1, 4):
            future_month = ((current_month + i - 1) % 12) + 1
            multiplier = self.pattern_db.get_demand_multiplier(category, future_month)
            predictions[future_month] = base_demand * multiplier
        
        return {
            "category": category.value,
            "pattern": pattern,
            "monthly_averages": monthly_averages,
            "predictions": predictions,
            "is_peak_season": self.pattern_db.is_peak_season(category, current_month),
            "current_multiplier": self.pattern_db.get_demand_multiplier(category, current_month)
        }
    
    def calculate_optimal_order_quantity(
        self, 
        item: InventoryItem, 
        demand_analysis: Dict[str, Any],
        supplier_info: Optional[SupplierInfo] = None
    ) -> Tuple[int, str]:
        """Calculate optimal order quantity based on seasonal patterns."""
        category = StationeryCategory(demand_analysis["category"])
        pattern = demand_analysis["pattern"]
        predictions = demand_analysis["predictions"]
        
        # Base calculation
        total_predicted_demand = sum(predictions.values())
        current_stock = item.current_stock
        safety_stock = item.min_stock_threshold * 1.5  # 50% buffer
        
        # Calculate order quantity
        order_quantity = max(0, total_predicted_demand + safety_stock - current_stock)
        
        # Apply seasonal adjustments
        if demand_analysis["is_peak_season"]:
            order_quantity = int(order_quantity * 1.2)  # 20% extra for peak season
            reasoning = f"Peak season ordering for {category.value}. Increased quantity by 20% to handle {pattern.description}"
        else:
            reasoning = f"Regular ordering for {category.value}. Based on 3-month demand forecast."
        
        # Consider supplier minimum order quantity
        if supplier_info and order_quantity < supplier_info.min_order_quantity:
            order_quantity = supplier_info.min_order_quantity
            reasoning += f" Adjusted to supplier minimum order quantity: {supplier_info.min_order_quantity}"
        
        # Round to reasonable quantities
        if order_quantity > 100:
            order_quantity = round(order_quantity / 10) * 10  # Round to nearest 10
        
        return order_quantity, reasoning
    
    def assess_urgency(
        self, 
        item: InventoryItem, 
        demand_analysis: Dict[str, Any]
    ) -> Priority:
        """Assess urgency based on stock levels and seasonal patterns."""
        category = StationeryCategory(demand_analysis["category"])
        current_month = datetime.now().month
        
        # Calculate days of stock remaining
        daily_demand = demand_analysis.get("current_multiplier", 1.0) * (item.min_stock_threshold / 30)
        days_remaining = item.current_stock / daily_demand if daily_demand > 0 else float('inf')
        
        # Educational calendar-based urgency
        critical_months = [3, 4, 5, 6, 7]  # Exam and school opening season
        in_critical_period = current_month in critical_months
        
        # Stock level assessment
        if item.current_stock == 0:
            return Priority.CRITICAL
        elif days_remaining <= item.lead_time_days:
            return Priority.CRITICAL if in_critical_period else Priority.HIGH
        elif days_remaining <= item.lead_time_days * 1.5:
            return Priority.HIGH
        elif demand_analysis["is_peak_season"] and days_remaining <= item.lead_time_days * 2:
            return Priority.HIGH
        elif days_remaining <= item.lead_time_days * 3:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def generate_negotiation_strategy(
        self, 
        items: List[InventoryItem], 
        supplier_info: Optional[SupplierInfo] = None
    ) -> Dict[str, Any]:
        """Generate supplier negotiation strategy for bulk stationery orders."""
        total_value = 0
        category_volumes = {}
        
        for item in items:
            category = self.categorize_stationery_item(item)
            if category not in category_volumes:
                category_volumes[category] = {"quantity": 0, "value": 0}
            
            category_volumes[category]["quantity"] += item.current_stock
            category_volumes[category]["value"] += item.current_stock * item.unit_cost
            total_value += item.current_stock * item.unit_cost
        
        # Negotiation points
        negotiation_points = []
        
        if total_value > 10000:
            negotiation_points.append("Leverage high order value for volume discount (target: 8-12%)")
        
        if len(category_volumes) >= 3:
            negotiation_points.append("Bundle multiple categories for cross-category discount")
        
        # Seasonal negotiation strategies
        current_month = datetime.now().month
        if current_month in [2, 3, 4]:  # Pre-season ordering
            negotiation_points.append("Early season ordering - negotiate for better pricing and guaranteed stock")
        elif current_month in [6, 7]:  # Peak season
            negotiation_points.append("Peak season order - prioritize delivery reliability over pricing")
        
        if supplier_info and supplier_info.reliability_score < 7:
            negotiation_points.append("Request reliability guarantees and penalty clauses for delays")
        
        return {
            "total_order_value": total_value,
            "category_breakdown": category_volumes,
            "negotiation_points": negotiation_points,
            "recommended_discount_target": min(15, max(5, total_value // 2000)),  # 5-15% based on volume
            "payment_terms": "45 days" if total_value > 15000 else "30 days"
        }
    
    def create_auto_order_decision(
        self, 
        item: InventoryItem, 
        sales_data: List[SalesData],
        supplier_info: Optional[SupplierInfo] = None
    ) -> AgentDecision:
        """Create automated order decision for stationery item."""
        current_month = datetime.now().month
        
        # Analyze seasonal demand
        demand_analysis = self.analyze_seasonal_demand(item, sales_data, current_month)
        
        # Calculate optimal order quantity
        order_quantity, quantity_reasoning = self.calculate_optimal_order_quantity(
            item, demand_analysis, supplier_info
        )
        
        # Assess urgency
        priority = self.assess_urgency(item, demand_analysis)
        
        # Determine action type
        if item.current_stock == 0:
            action_type = ActionType.RESTOCK  # Emergency restock
        elif demand_analysis["is_peak_season"]:
            action_type = ActionType.RESTOCK  # Seasonal restock
        elif order_quantity > 0:
            action_type = ActionType.RESTOCK  # Regular restock
        else:
            action_type = ActionType.HOLD  # Hold current stock
        
        # Calculate estimated cost
        estimated_cost = order_quantity * item.unit_cost if order_quantity > 0 else 0
        
        # Calculate deadline
        lead_time_adjustment = demand_analysis["pattern"].lead_time_adjustment
        adjusted_lead_time = max(1, item.lead_time_days + lead_time_adjustment)
        deadline = datetime.now() + timedelta(days=adjusted_lead_time)
        
        # Build reasoning
        reasoning_parts = [
            f"Stationery Analysis for {demand_analysis['category'].replace('_', ' ').title()}:",
            f"- {quantity_reasoning}",
            f"- Current stock: {item.current_stock}, Min threshold: {item.min_stock_threshold}",
            f"- Seasonal context: {demand_analysis['pattern'].description}",
        ]
        
        if demand_analysis["is_peak_season"]:
            reasoning_parts.append(f"- PEAK SEASON: {demand_analysis['current_multiplier']:.1f}x demand multiplier")
        
        if supplier_info:
            reasoning_parts.append(f"- Supplier: {supplier_info.name} (Reliability: {supplier_info.reliability_score}/10)")
        
        reasoning = "\n".join(reasoning_parts)
        
        # Calculate confidence score
        confidence = 0.8
        if demand_analysis["monthly_averages"]:
            confidence += 0.1  # More confidence with historical data
        if demand_analysis["is_peak_season"]:
            confidence += 0.05  # More confidence in peak season decisions
        confidence = min(0.95, confidence)
        
        return AgentDecision(
            agent_role=self.agent_role,
            item_sku=item.sku,
            action_type=action_type,
            priority=priority,
            confidence_score=confidence,
            reasoning=reasoning,
            recommended_quantity=order_quantity if order_quantity > 0 else None,
            estimated_cost=estimated_cost if estimated_cost > 0 else None,
            deadline=deadline,
            metadata={
                "category": demand_analysis["category"],
                "seasonal_analysis": demand_analysis,
                "is_auto_generated": True,
                "education_calendar_aware": True
            }
        )
    
    def analyze_stationery_portfolio(
        self, 
        inventory_items: List[InventoryItem], 
        sales_data: List[SalesData],
        supplier_data: Optional[List[SupplierInfo]] = None
    ) -> List[AgentDecision]:
        """Comprehensive analysis of entire stationery inventory portfolio."""
        decisions = []
        supplier_map = {s.name: s for s in supplier_data} if supplier_data else {}
        
        logger.info(f"Analyzing stationery portfolio with {len(inventory_items)} items")
        
        # Group items by category for bulk analysis
        category_items = {}
        for item in inventory_items:
            category = self.categorize_stationery_item(item)
            if category not in category_items:
                category_items[category] = []
            category_items[category].append(item)
        
        # Generate decisions for each item
        for item in inventory_items:
            supplier_info = supplier_map.get(item.supplier_id) if item.supplier_id else None
            decision = self.create_auto_order_decision(item, sales_data, supplier_info)
            decisions.append(decision)
        
        # Sort decisions by priority and estimated impact
        decisions.sort(key=lambda d: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}[d.priority.value],
            d.estimated_cost or 0
        ), reverse=True)
        
        logger.info(f"Generated {len(decisions)} stationery management decisions")
        
        return decisions
    
    def get_dashboard_insights(
        self, 
        inventory_items: List[InventoryItem], 
        sales_data: List[SalesData]
    ) -> Dict[str, Any]:
        """Generate dashboard insights for stationery inventory."""
        current_month = datetime.now().month
        category_stats = {}
        total_value = 0
        critical_items = []
        seasonal_opportunities = []
        
        for item in inventory_items:
            category = self.categorize_stationery_item(item)
            
            if category not in category_stats:
                category_stats[category.value] = {
                    "items_count": 0,
                    "total_stock": 0,
                    "total_value": 0,
                    "low_stock_items": 0
                }
            
            stats = category_stats[category.value]
            stats["items_count"] += 1
            stats["total_stock"] += item.current_stock
            stats["total_value"] += item.current_stock * item.unit_cost
            total_value += item.current_stock * item.unit_cost
            
            if item.current_stock <= item.min_stock_threshold:
                stats["low_stock_items"] += 1
                critical_items.append({
                    "sku": item.sku,
                    "name": item.name,
                    "category": category.value,
                    "current_stock": item.current_stock,
                    "min_threshold": item.min_stock_threshold
                })
            
            # Check for seasonal opportunities
            if self.pattern_db.is_peak_season(category, current_month):
                seasonal_opportunities.append({
                    "sku": item.sku,
                    "name": item.name,
                    "category": category.value,
                    "opportunity": f"Peak season for {category.value.replace('_', ' ')}"
                })
        
        # Educational calendar insights
        calendar_insights = []
        if current_month in [3, 4, 5]:
            calendar_insights.append("School preparation season - focus on textbooks and essentials")
        elif current_month in [6, 7]:
            calendar_insights.append("Back-to-school rush - all categories high demand")
        elif current_month in [11, 12]:
            calendar_insights.append("Exam season - writing instruments and paper products priority")
        
        return {
            "total_inventory_value": total_value,
            "category_breakdown": category_stats,
            "critical_items_count": len(critical_items),
            "critical_items": critical_items[:10],  # Top 10
            "seasonal_opportunities": seasonal_opportunities,
            "calendar_insights": calendar_insights,
            "health_score": max(0, 100 - len(critical_items) * 5),
            "next_peak_season": self._get_next_peak_season(current_month)
        }
    
    def _get_next_peak_season(self, current_month: int) -> Dict[str, Any]:
        """Get information about the next peak season."""
        peak_seasons = [
            (4, "School Preparation (April-June)"),
            (6, "Back-to-School Rush (June-July)"),
            (11, "Exam Season (November-December)"),
            (1, "New Year Session (January)")
        ]
        
        for month, description in peak_seasons:
            if month > current_month:
                return {"month": month, "description": description}
        
        # If no peak season left in current year, return first of next year
        return {"month": 1, "description": "New Year Session (January)"}


# Factory function to create the agent
def create_stationery_agent() -> StationeryInventoryAgent:
    """Factory function to create stationery inventory agent."""
    return StationeryInventoryAgent()