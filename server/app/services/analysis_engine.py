import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.core.logging import logger


class AnalysisType(Enum):
    STOCK_LEVEL = "stock_level"
    SALES_TREND = "sales_trend"
    DEMAND_FORECAST = "demand_forecast"
    VENDOR_PERFORMANCE = "vendor_performance"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class AnalysisResult:
    """Standardized result structure for all analyses"""
    analysis_type: AnalysisType
    item_id: Optional[int]
    timestamp: datetime
    confidence: float
    data: Dict[str, Any]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]


class StockAnalyzer:
    """Analyze stock levels and generate reorder recommendations"""
    
    @staticmethod
    def analyze_stock_status(inventory_items: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze current stock status across all items"""
        
        critical_items = []
        warning_items = []
        overstock_items = []
        
        for item in inventory_items:
            current_stock = item.get("current_stock", 0)
            reorder_level = item.get("reorder_level", 0)
            max_stock = item.get("max_stock_level", 100)
            
            # Calculate stock percentage
            stock_percentage = (current_stock / max_stock) * 100 if max_stock > 0 else 0
            
            if current_stock <= 0:
                critical_items.append({
                    **item,
                    "status": "out_of_stock",
                    "priority": "critical",
                    "stock_percentage": 0
                })
            elif current_stock <= reorder_level:
                critical_items.append({
                    **item,
                    "status": "below_reorder_level",
                    "priority": "high",
                    "stock_percentage": stock_percentage
                })
            elif current_stock <= reorder_level * 1.5:
                warning_items.append({
                    **item,
                    "status": "approaching_reorder",
                    "priority": "medium",
                    "stock_percentage": stock_percentage
                })
            elif stock_percentage > 120:  # 20% above max stock
                overstock_items.append({
                    **item,
                    "status": "overstock",
                    "priority": "low",
                    "stock_percentage": stock_percentage
                })
        
        # Generate recommendations
        recommendations = []
        if critical_items:
            recommendations.append(f"Immediate reorder required for {len(critical_items)} critical items")
        if warning_items:
            recommendations.append(f"Monitor {len(warning_items)} items approaching reorder level")
        if overstock_items:
            recommendations.append(f"Review {len(overstock_items)} overstocked items")
        
        # Generate alerts
        alerts = []
        for item in critical_items:
            alerts.append({
                "type": "stock_alert",
                "severity": "high" if item["current_stock"] <= 0 else "medium",
                "item_id": item["id"],
                "sku": item["sku"],
                "message": f"{item['name']} is {'out of stock' if item['current_stock'] <= 0 else 'below reorder level'}"
            })
        
        return AnalysisResult(
            analysis_type=AnalysisType.STOCK_LEVEL,
            item_id=None,
            timestamp=datetime.utcnow(),
            confidence=0.95,  # High confidence for stock level analysis
            data={
                "total_items": len(inventory_items),
                "critical_items": critical_items,
                "warning_items": warning_items,
                "overstock_items": overstock_items,
                "summary": {
                    "critical_count": len(critical_items),
                    "warning_count": len(warning_items),
                    "overstock_count": len(overstock_items),
                    "healthy_count": len(inventory_items) - len(critical_items) - len(warning_items) - len(overstock_items)
                }
            },
            recommendations=recommendations,
            alerts=alerts
        )
    
    @staticmethod
    def calculate_reorder_quantity(
        item: Dict[str, Any], 
        sales_history: List[Dict[str, Any]],
        lead_time_days: int = 7
    ) -> Tuple[int, float]:
        """Calculate optimal reorder quantity using sales velocity"""
        
        if not sales_history:
            # Fallback to basic reorder quantity
            safety_stock = item.get("reorder_level", 10)
            max_stock = item.get("max_stock_level", 100)
            return min(max_stock - item.get("current_stock", 0), safety_stock * 2), 0.5
        
        # Calculate daily sales velocity
        df = pd.DataFrame(sales_history)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Group by date and sum quantities
        daily_sales = df.groupby(df['sale_date'].dt.date)['quantity_sold'].sum()
        
        if len(daily_sales) == 0:
            return item.get("reorder_level", 10), 0.3
        
        # Calculate average daily sales
        avg_daily_sales = daily_sales.mean()
        
        # Calculate safety stock (buffer for variability)
        sales_std = daily_sales.std() if len(daily_sales) > 1 else avg_daily_sales * 0.2
        safety_stock = max(sales_std * 2, avg_daily_sales * 0.5)  # 2 std devs or 50% of daily avg
        
        # Calculate reorder quantity
        lead_time_demand = avg_daily_sales * lead_time_days
        reorder_quantity = lead_time_demand + safety_stock
        
        # Ensure we don't exceed max stock
        current_stock = item.get("current_stock", 0)
        max_stock = item.get("max_stock_level", 100)
        available_capacity = max_stock - current_stock
        
        final_quantity = min(int(reorder_quantity), available_capacity)
        
        # Calculate confidence based on data quality
        confidence = min(0.9, 0.5 + (len(daily_sales) / 30))  # More data = higher confidence
        
        return max(final_quantity, 1), confidence


class SalesTrendAnalyzer:
    """Analyze sales trends and patterns"""
    
    @staticmethod
    def analyze_sales_trends(sales_data: List[Dict[str, Any]], days: int = 30) -> AnalysisResult:
        """Analyze sales trends over specified period"""
        
        if not sales_data:
            return AnalysisResult(
                analysis_type=AnalysisType.SALES_TREND,
                item_id=None,
                timestamp=datetime.utcnow(),
                confidence=0.1,
                data={"error": "No sales data available"},
                recommendations=["Investigate lack of sales data"],
                alerts=[{
                    "type": "data_alert",
                    "severity": "medium",
                    "message": "No sales data available for trend analysis"
                }]
            )
        
        df = pd.DataFrame(sales_data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Filter to recent period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_sales = df[df['sale_date'] >= cutoff_date]
        
        # Daily aggregation
        daily_stats = recent_sales.groupby(recent_sales['sale_date'].dt.date).agg({
            'quantity_sold': 'sum',
            'total_amount': 'sum',
            'id': 'count'  # transaction count
        }).rename(columns={'id': 'transaction_count'})
        
        # Calculate trends
        trend_analysis = SalesTrendAnalyzer._calculate_trend_metrics(daily_stats)
        
        # Item-level analysis
        item_trends = recent_sales.groupby('item_id').agg({
            'quantity_sold': 'sum',
            'total_amount': 'sum'
        }).sort_values('quantity_sold', ascending=False)
        
        recommendations = []
        alerts = []
        
        # Generate insights
        if trend_analysis['trend'] == 'increasing':
            recommendations.append("Sales trending upward - consider increasing stock levels")
        elif trend_analysis['trend'] == 'decreasing':
            recommendations.append("Sales declining - investigate causes and adjust inventory")
            alerts.append({
                "type": "trend_alert",
                "severity": "medium",
                "message": f"Sales declined by {abs(trend_analysis['change_percentage']):.1f}% over {days} days"
            })
        
        return AnalysisResult(
            analysis_type=AnalysisType.SALES_TREND,
            item_id=None,
            timestamp=datetime.utcnow(),
            confidence=min(0.9, len(daily_stats) / 30),  # Confidence based on data points
            data={
                "period_days": days,
                "total_sales": recent_sales['quantity_sold'].sum(),
                "total_revenue": recent_sales['total_amount'].sum(),
                "daily_stats": daily_stats.to_dict('index'),
                "trend_analysis": trend_analysis,
                "top_items": item_trends.head(10).to_dict('index'),
                "data_quality": {
                    "total_records": len(recent_sales),
                    "date_range": {
                        "start": recent_sales['sale_date'].min().isoformat() if not recent_sales.empty else None,
                        "end": recent_sales['sale_date'].max().isoformat() if not recent_sales.empty else None
                    }
                }
            },
            recommendations=recommendations,
            alerts=alerts
        )
    
    @staticmethod
    def _calculate_trend_metrics(daily_stats: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend metrics from daily sales data"""
        
        if len(daily_stats) < 3:
            return {
                "trend": "insufficient_data",
                "change_percentage": 0,
                "volatility": 0,
                "confidence": 0.1
            }
        
        # Calculate linear trend
        x = np.arange(len(daily_stats))
        y = daily_stats['quantity_sold'].values
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate percentage change
        start_value = daily_stats['quantity_sold'].iloc[:3].mean()  # First 3 days average
        end_value = daily_stats['quantity_sold'].iloc[-3:].mean()   # Last 3 days average
        
        change_percentage = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0
        
        # Determine trend direction
        if abs(change_percentage) < 5:
            trend = "stable"
        elif change_percentage > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Calculate volatility (coefficient of variation)
        volatility = (daily_stats['quantity_sold'].std() / daily_stats['quantity_sold'].mean()) if daily_stats['quantity_sold'].mean() > 0 else 0
        
        return {
            "trend": trend,
            "slope": slope,
            "change_percentage": change_percentage,
            "volatility": volatility,
            "confidence": min(0.9, len(daily_stats) / 30)
        }


class AnomalyDetector:
    """Detect anomalies in sales and inventory data"""
    
    @staticmethod
    def detect_sales_anomalies(
        sales_data: List[Dict[str, Any]], 
        item_id: Optional[int] = None,
        threshold: float = 2.0
    ) -> AnalysisResult:
        """Detect anomalies in sales patterns using statistical methods"""
        
        if not sales_data:
            return AnomalyDetector._empty_anomaly_result()
        
        df = pd.DataFrame(sales_data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Filter by item if specified
        if item_id:
            df = df[df['item_id'] == item_id]
        
        if len(df) < 7:  # Need at least a week of data
            return AnomalyDetector._empty_anomaly_result("Insufficient data for anomaly detection")
        
        # Daily aggregation
        daily_sales = df.groupby(df['sale_date'].dt.date)['quantity_sold'].sum()
        
        # Z-score based anomaly detection
        mean_sales = daily_sales.mean()
        std_sales = daily_sales.std()
        
        anomalies = []
        alerts = []
        
        if std_sales > 0:
            for date, sales in daily_sales.items():
                z_score = abs((sales - mean_sales) / std_sales)
                
                if z_score > threshold:
                    anomaly_type = "sales_spike" if sales > mean_sales else "sales_drop"
                    severity = "high" if z_score > 3 else "medium"
                    
                    anomaly = {
                        "date": date.isoformat(),
                        "sales": sales,
                        "z_score": z_score,
                        "type": anomaly_type,
                        "severity": severity,
                        "expected_range": [
                            max(0, mean_sales - std_sales * threshold),
                            mean_sales + std_sales * threshold
                        ]
                    }
                    anomalies.append(anomaly)
                    
                    alerts.append({
                        "type": "anomaly_alert",
                        "severity": severity,
                        "item_id": item_id,
                        "message": f"Unusual {anomaly_type} detected on {date}: {sales} units (z-score: {z_score:.2f})"
                    })
        
        # Moving average based detection for trends
        if len(daily_sales) >= 14:
            window = 7
            ma = daily_sales.rolling(window=window).mean()
            recent_avg = daily_sales.tail(3).mean()
            trend_baseline = ma.iloc[-window-1:-1].mean()  # Previous week's MA
            
            if abs(recent_avg - trend_baseline) > std_sales * threshold:
                trend_anomaly = {
                    "type": "trend_shift",
                    "recent_average": recent_avg,
                    "baseline_average": trend_baseline,
                    "deviation": recent_avg - trend_baseline,
                    "severity": "high" if abs(recent_avg - trend_baseline) > std_sales * 3 else "medium"
                }
                anomalies.append(trend_anomaly)
        
        recommendations = []
        if anomalies:
            recommendations.append(f"Investigate {len(anomalies)} detected anomalies")
            recommendations.append("Review external factors that might affect sales")
        else:
            recommendations.append("Sales patterns appear normal")
        
        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            item_id=item_id,
            timestamp=datetime.utcnow(),
            confidence=min(0.9, len(daily_sales) / 30),
            data={
                "anomalies": anomalies,
                "statistics": {
                    "mean_sales": mean_sales,
                    "std_sales": std_sales,
                    "total_days": len(daily_sales),
                    "anomaly_count": len(anomalies)
                },
                "threshold": threshold
            },
            recommendations=recommendations,
            alerts=alerts
        )
    
    @staticmethod
    def _empty_anomaly_result(reason: str = "No data available") -> AnalysisResult:
        """Return empty anomaly result"""
        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            item_id=None,
            timestamp=datetime.utcnow(),
            confidence=0.1,
            data={"error": reason},
            recommendations=[f"Cannot perform anomaly detection: {reason}"],
            alerts=[]
        )


class DemandForecaster:
    """Simple demand forecasting using statistical methods"""
    
    @staticmethod
    def forecast_demand(
        sales_data: List[Dict[str, Any]], 
        item_id: int,
        forecast_days: int = 30
    ) -> AnalysisResult:
        """Forecast demand for specified number of days"""
        
        if not sales_data:
            return DemandForecaster._empty_forecast_result(item_id)
        
        df = pd.DataFrame(sales_data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df = df[df['item_id'] == item_id]
        
        if len(df) < 7:
            return DemandForecaster._empty_forecast_result(item_id, "Insufficient historical data")
        
        # Daily aggregation
        daily_sales = df.groupby(df['sale_date'].dt.date)['quantity_sold'].sum()
        daily_sales = daily_sales.reindex(
            pd.date_range(start=daily_sales.index.min(), end=daily_sales.index.max(), freq='D'),
            fill_value=0
        )
        
        # Simple forecasting methods
        forecasts = {}
        
        # 1. Moving average forecast
        window = min(7, len(daily_sales) // 2)
        ma_forecast = daily_sales.rolling(window=window).mean().iloc[-1]
        forecasts['moving_average'] = ma_forecast * forecast_days
        
        # 2. Linear trend forecast
        x = np.arange(len(daily_sales))
        y = daily_sales.values
        slope, intercept = np.polyfit(x, y, 1)
        
        future_x = np.arange(len(daily_sales), len(daily_sales) + forecast_days)
        trend_forecast = sum(slope * fx + intercept for fx in future_x)
        forecasts['linear_trend'] = max(0, trend_forecast)
        
        # 3. Seasonal naive (if enough data)
        if len(daily_sales) >= 14:
            seasonal_pattern = daily_sales.iloc[-7:].mean()  # Last week average
            forecasts['seasonal'] = seasonal_pattern * forecast_days
        
        # Ensemble forecast (average of available methods)
        ensemble_forecast = np.mean(list(forecasts.values()))
        
        # Calculate confidence based on historical variance
        historical_variance = daily_sales.var()
        confidence = max(0.3, min(0.9, 1 / (1 + historical_variance / daily_sales.mean())))
        
        recommendations = [
            f"Expected demand: {ensemble_forecast:.1f} units over {forecast_days} days",
            f"Daily average: {ensemble_forecast / forecast_days:.1f} units"
        ]
        
        return AnalysisResult(
            analysis_type=AnalysisType.DEMAND_FORECAST,
            item_id=item_id,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            data={
                "forecast_period_days": forecast_days,
                "forecasts": forecasts,
                "ensemble_forecast": ensemble_forecast,
                "daily_average_forecast": ensemble_forecast / forecast_days,
                "historical_stats": {
                    "mean": daily_sales.mean(),
                    "std": daily_sales.std(),
                    "min": daily_sales.min(),
                    "max": daily_sales.max()
                }
            },
            recommendations=recommendations,
            alerts=[]
        )
    
    @staticmethod
    def _empty_forecast_result(item_id: int, reason: str = "No sales data") -> AnalysisResult:
        """Return empty forecast result"""
        return AnalysisResult(
            analysis_type=AnalysisType.DEMAND_FORECAST,
            item_id=item_id,
            timestamp=datetime.utcnow(),
            confidence=0.1,
            data={"error": reason},
            recommendations=[f"Cannot forecast demand: {reason}"],
            alerts=[]
        )


class VendorAnalyzer:
    """Analyze vendor performance and risks"""
    
    @staticmethod
    def analyze_vendor_performance(vendor_data: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze vendor performance metrics"""
        
        if not vendor_data:
            return AnalysisResult(
                analysis_type=AnalysisType.VENDOR_PERFORMANCE,
                item_id=None,
                timestamp=datetime.utcnow(),
                confidence=0.1,
                data={"error": "No vendor data available"},
                recommendations=["Set up vendor performance tracking"],
                alerts=[]
            )
        
        performance_analysis = []
        alerts = []
        
        for vendor in vendor_data:
            vendor_id = vendor.get("id")
            reliability_score = vendor.get("reliability_score", 5.0)
            avg_delivery_days = vendor.get("avg_delivery_days", 7)
            
            # Performance scoring
            performance_score = min(10, reliability_score * (7 / max(avg_delivery_days, 1)))
            
            risk_level = "low"
            if performance_score < 4:
                risk_level = "high"
            elif performance_score < 6:
                risk_level = "medium"
            
            vendor_analysis = {
                "vendor_id": vendor_id,
                "name": vendor.get("name", "Unknown"),
                "reliability_score": reliability_score,
                "avg_delivery_days": avg_delivery_days,
                "performance_score": performance_score,
                "risk_level": risk_level,
                "status": vendor.get("status", "unknown")
            }
            
            performance_analysis.append(vendor_analysis)
            
            # Generate alerts for poor performers
            if risk_level == "high":
                alerts.append({
                    "type": "vendor_risk",
                    "severity": "high",
                    "vendor_id": vendor_id,
                    "message": f"Vendor {vendor.get('name')} has poor performance (score: {performance_score:.1f})"
                })
        
        # Sort by performance score
        performance_analysis.sort(key=lambda x: x["performance_score"], reverse=True)
        
        recommendations = []
        high_risk_count = sum(1 for v in performance_analysis if v["risk_level"] == "high")
        if high_risk_count > 0:
            recommendations.append(f"Review {high_risk_count} high-risk vendors")
            recommendations.append("Consider diversifying supplier base")
        
        return AnalysisResult(
            analysis_type=AnalysisType.VENDOR_PERFORMANCE,
            item_id=None,
            timestamp=datetime.utcnow(),
            confidence=0.85,
            data={
                "vendor_analysis": performance_analysis,
                "summary": {
                    "total_vendors": len(vendor_data),
                    "high_risk": sum(1 for v in performance_analysis if v["risk_level"] == "high"),
                    "medium_risk": sum(1 for v in performance_analysis if v["risk_level"] == "medium"),
                    "low_risk": sum(1 for v in performance_analysis if v["risk_level"] == "low"),
                }
            },
            recommendations=recommendations,
            alerts=alerts
        )