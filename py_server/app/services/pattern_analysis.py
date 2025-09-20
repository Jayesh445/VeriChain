"""
Advanced pattern analysis for stationery inventory management.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import statistics

from pydantic import BaseModel
from loguru import logger

from app.models import InventoryItem, SalesData, SupplierInfo
from app.agents.stationery_agent import StationeryCategory, StationeryPatternDatabase


@dataclass
class PatternInsight:
    """Pattern analysis insight."""
    insight_type: str
    confidence: float
    description: str
    impact: str
    recommendation: str
    data_points: int
    discovered_at: datetime


class EducationalCalendarAnalyzer:
    """
    Analyzes patterns based on educational calendar events.
    """
    
    EDUCATIONAL_EVENTS = {
        "school_opening": {"months": [6, 7], "impact_factor": 3.0},
        "mid_session": {"months": [9, 10], "impact_factor": 1.5},
        "exam_preparation": {"months": [11, 12, 3, 4], "impact_factor": 2.5},
        "new_session": {"months": [1], "impact_factor": 2.0},
        "admission_season": {"months": [4, 5], "impact_factor": 1.8},
        "holiday_season": {"months": [12], "impact_factor": 0.7}
    }
    
    @classmethod
    def get_event_for_month(cls, month: int) -> Optional[str]:
        """Get the primary educational event for a given month."""
        for event, data in cls.EDUCATIONAL_EVENTS.items():
            if month in data["months"]:
                return event
        return None
    
    @classmethod
    def get_impact_factor(cls, month: int) -> float:
        """Get the impact factor for a given month."""
        event = cls.get_event_for_month(month)
        if event:
            return cls.EDUCATIONAL_EVENTS[event]["impact_factor"]
        return 1.0


class DemandPatternAnalyzer:
    """
    Analyzes demand patterns in stationery sales data.
    """
    
    def __init__(self):
        self.insights: List[PatternInsight] = []
        logger.info("Initialized Demand Pattern Analyzer")
    
    def analyze_seasonal_patterns(
        self, 
        sales_data: List[SalesData], 
        item: InventoryItem
    ) -> List[PatternInsight]:
        """Analyze seasonal demand patterns for an item."""
        insights = []
        
        # Group sales by month
        monthly_sales = defaultdict(list)
        for sale in sales_data:
            if sale.sku == item.sku:
                monthly_sales[sale.date.month].append(sale.quantity_sold)
        
        if len(monthly_sales) < 3:
            return insights  # Not enough data
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, sales in monthly_sales.items():
            monthly_averages[month] = statistics.mean(sales)
        
        # Detect seasonal spikes
        overall_average = statistics.mean(monthly_averages.values())
        seasonal_spikes = []
        
        for month, avg_sales in monthly_averages.items():
            if avg_sales > overall_average * 1.5:  # 50% above average
                seasonal_spikes.append((month, avg_sales, avg_sales / overall_average))
        
        # Generate insights for spikes
        for month, sales, multiplier in seasonal_spikes:
            event = EducationalCalendarAnalyzer.get_event_for_month(month)
            event_name = event.replace('_', ' ').title() if event else "Unknown Event"
            
            insight = PatternInsight(
                insight_type="seasonal_spike",
                confidence=min(0.95, 0.6 + (multiplier - 1.5) * 0.2),
                description=f"{item.name} shows {multiplier:.1f}x higher demand in {datetime(2024, month, 1).strftime('%B')}",
                impact=f"Potential stockout risk during {event_name}",
                recommendation=f"Increase stock by {int((multiplier - 1) * 100)}% before {event_name}",
                data_points=len(monthly_sales[month]),
                discovered_at=datetime.utcnow()
            )
            insights.append(insight)
        
        return insights
    
    def analyze_weekly_patterns(self, sales_data: List[SalesData]) -> List[PatternInsight]:
        """Analyze weekly patterns across all items."""
        insights = []
        
        # Group sales by day of week
        daily_sales = defaultdict(list)
        for sale in sales_data:
            day_of_week = sale.date.weekday()  # 0 = Monday, 6 = Sunday
            daily_sales[day_of_week].append(sale.quantity_sold)
        
        if len(daily_sales) < 5:
            return insights
        
        # Calculate daily averages
        daily_averages = {}
        for day, sales in daily_sales.items():
            daily_averages[day] = statistics.mean(sales)
        
        overall_average = statistics.mean(daily_averages.values())
        
        # Detect patterns
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day, avg_sales in daily_averages.items():
            if avg_sales > overall_average * 1.3:  # 30% above average
                insight = PatternInsight(
                    insight_type="weekly_pattern",
                    confidence=0.7,
                    description=f"Higher sales volume on {weekday_names[day]}s",
                    impact="Inventory planning opportunity",
                    recommendation=f"Schedule restocking before {weekday_names[day]}s",
                    data_points=len(daily_sales[day]),
                    discovered_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def analyze_trend_patterns(self, sales_data: List[SalesData]) -> List[PatternInsight]:
        """Analyze long-term trend patterns."""
        insights = []
        
        # Group sales by month and year
        monthly_totals = defaultdict(int)
        for sale in sales_data:
            month_key = sale.date.strftime("%Y-%m")
            monthly_totals[month_key] += sale.quantity_sold
        
        if len(monthly_totals) < 6:
            return insights
        
        # Sort by date and calculate trend
        sorted_months = sorted(monthly_totals.items())
        values = [total for _, total in sorted_months]
        
        # Simple trend analysis
        if len(values) >= 6:
            first_half = statistics.mean(values[:len(values)//2])
            second_half = statistics.mean(values[len(values)//2:])
            
            if second_half > first_half * 1.2:  # 20% growth
                insight = PatternInsight(
                    insight_type="growth_trend",
                    confidence=0.8,
                    description=f"Upward sales trend: {((second_half/first_half - 1) * 100):.1f}% growth",
                    impact="Increased demand requiring higher inventory levels",
                    recommendation="Adjust reorder points and safety stock levels",
                    data_points=len(values),
                    discovered_at=datetime.utcnow()
                )
                insights.append(insight)
            
            elif second_half < first_half * 0.8:  # 20% decline
                insight = PatternInsight(
                    insight_type="decline_trend",
                    confidence=0.8,
                    description=f"Declining sales trend: {((1 - second_half/first_half) * 100):.1f}% decline",
                    impact="Potential overstock situation",
                    recommendation="Reduce reorder quantities and review product relevance",
                    data_points=len(values),
                    discovered_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def analyze_category_correlations(
        self, 
        sales_data: List[SalesData], 
        inventory_items: List[InventoryItem]
    ) -> List[PatternInsight]:
        """Analyze correlations between different stationery categories."""
        insights = []
        
        from app.agents.stationery_agent import StationeryInventoryAgent
        agent = StationeryInventoryAgent()
        
        # Group items by category
        category_sales = defaultdict(lambda: defaultdict(int))
        
        for sale in sales_data:
            # Find the item to get its category
            item = next((i for i in inventory_items if i.sku == sale.sku), None)
            if item:
                category = agent.categorize_stationery_item(item)
                month_key = sale.date.strftime("%Y-%m")
                category_sales[category.value][month_key] += sale.quantity_sold
        
        # Analyze correlations between categories
        categories = list(category_sales.keys())
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                correlation = self._calculate_correlation(
                    category_sales[cat1], 
                    category_sales[cat2]
                )
                
                if correlation > 0.7:  # Strong positive correlation
                    insight = PatternInsight(
                        insight_type="category_correlation",
                        confidence=correlation,
                        description=f"Strong correlation between {cat1} and {cat2} sales",
                        impact="Cross-category demand dependency",
                        recommendation=f"Bundle ordering for {cat1} and {cat2}",
                        data_points=len(set(category_sales[cat1].keys()) & set(category_sales[cat2].keys())),
                        discovered_at=datetime.utcnow()
                    )
                    insights.append(insight)
        
        return insights
    
    def _calculate_correlation(
        self, 
        series1: Dict[str, int], 
        series2: Dict[str, int]
    ) -> float:
        """Calculate correlation between two time series."""
        common_keys = set(series1.keys()) & set(series2.keys())
        
        if len(common_keys) < 3:
            return 0.0
        
        values1 = [series1[key] for key in common_keys]
        values2 = [series2[key] for key in common_keys]
        
        try:
            return statistics.correlation(values1, values2)
        except:
            return 0.0
    
    def detect_anomalies(self, sales_data: List[SalesData]) -> List[PatternInsight]:
        """Detect anomalous sales patterns."""
        insights = []
        
        # Group by SKU and date
        sku_daily_sales = defaultdict(lambda: defaultdict(int))
        for sale in sales_data:
            date_key = sale.date.strftime("%Y-%m-%d")
            sku_daily_sales[sale.sku][date_key] += sale.quantity_sold
        
        for sku, daily_sales in sku_daily_sales.items():
            if len(daily_sales) < 10:
                continue
            
            values = list(daily_sales.values())
            mean_sales = statistics.mean(values)
            
            if len(values) > 1:
                std_dev = statistics.stdev(values)
                
                # Detect outliers (sales > mean + 2*std_dev)
                outliers = [v for v in values if v > mean_sales + 2 * std_dev]
                
                if outliers and max(outliers) > mean_sales * 3:  # Very high spike
                    insight = PatternInsight(
                        insight_type="demand_anomaly",
                        confidence=0.9,
                        description=f"Unusual demand spike for {sku}: {max(outliers)} units (avg: {mean_sales:.1f})",
                        impact="Potential stockout during unexpected demand",
                        recommendation="Investigate cause and adjust safety stock",
                        data_points=len(values),
                        discovered_at=datetime.utcnow()
                    )
                    insights.append(insight)
        
        return insights
    
    def generate_comprehensive_analysis(
        self, 
        sales_data: List[SalesData], 
        inventory_items: List[InventoryItem]
    ) -> Dict[str, Any]:
        """Generate comprehensive pattern analysis."""
        all_insights = []
        
        # Analyze patterns for each item
        for item in inventory_items:
            item_sales = [s for s in sales_data if s.sku == item.sku]
            if item_sales:
                seasonal_insights = self.analyze_seasonal_patterns(item_sales, item)
                all_insights.extend(seasonal_insights)
        
        # Analyze overall patterns
        weekly_insights = self.analyze_weekly_patterns(sales_data)
        trend_insights = self.analyze_trend_patterns(sales_data)
        correlation_insights = self.analyze_category_correlations(sales_data, inventory_items)
        anomaly_insights = self.detect_anomalies(sales_data)
        
        all_insights.extend(weekly_insights)
        all_insights.extend(trend_insights)
        all_insights.extend(correlation_insights)
        all_insights.extend(anomaly_insights)
        
        # Sort by confidence and impact
        all_insights.sort(key=lambda x: x.confidence, reverse=True)
        
        # Group insights by type
        insights_by_type = defaultdict(list)
        for insight in all_insights:
            insights_by_type[insight.insight_type].append(insight)
        
        # Generate summary statistics
        high_confidence_insights = [i for i in all_insights if i.confidence > 0.8]
        actionable_insights = [i for i in all_insights if "adjust" in i.recommendation.lower() or "increase" in i.recommendation.lower()]
        
        return {
            "total_insights": len(all_insights),
            "high_confidence_insights": len(high_confidence_insights),
            "actionable_insights": len(actionable_insights),
            "insights_by_type": {k: len(v) for k, v in insights_by_type.items()},
            "top_insights": [
                {
                    "type": insight.insight_type,
                    "confidence": insight.confidence,
                    "description": insight.description,
                    "impact": insight.impact,
                    "recommendation": insight.recommendation,
                    "data_points": insight.data_points
                }
                for insight in all_insights[:10]
            ],
            "pattern_summary": self._generate_pattern_summary(all_insights),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_pattern_summary(self, insights: List[PatternInsight]) -> str:
        """Generate a summary of discovered patterns."""
        if not insights:
            return "No significant patterns detected in the data."
        
        summary_parts = []
        
        # Count by type
        type_counts = defaultdict(int)
        for insight in insights:
            type_counts[insight.insight_type] += 1
        
        if type_counts.get("seasonal_spike", 0) > 0:
            summary_parts.append(f"Detected {type_counts['seasonal_spike']} seasonal demand spikes")
        
        if type_counts.get("growth_trend", 0) > 0:
            summary_parts.append(f"Identified {type_counts['growth_trend']} growth trends")
        
        if type_counts.get("category_correlation", 0) > 0:
            summary_parts.append(f"Found {type_counts['category_correlation']} category correlations")
        
        if type_counts.get("demand_anomaly", 0) > 0:
            summary_parts.append(f"Detected {type_counts['demand_anomaly']} demand anomalies")
        
        high_confidence = len([i for i in insights if i.confidence > 0.8])
        summary_parts.append(f"{high_confidence} high-confidence insights")
        
        return ". ".join(summary_parts) + "."


# Factory function
def create_pattern_analyzer() -> DemandPatternAnalyzer:
    """Create a demand pattern analyzer instance."""
    return DemandPatternAnalyzer()