from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.database import (
    InventoryService, SalesService, VendorService, OrderService, AgentDecisionService
)
from app.models import DashboardData
from app.core.logging import logger

router = APIRouter()


@router.get("/scm", response_model=Dict[str, Any])
async def get_scm_dashboard(db: AsyncSession = Depends(get_db)):
    """
    Supply Chain Manager dashboard
    Focus on operational metrics, stock levels, and urgent actions
    """
    try:
        # Get inventory summary
        inventory_summary = await InventoryService.get_inventory_summary(db)
        
        # Get critical items
        low_stock_items = await InventoryService.get_low_stock_items(db)
        out_of_stock_items = await InventoryService.get_out_of_stock_items(db)
        
        # Get pending orders
        pending_orders = await OrderService.get_pending_orders(db)
        
        # Get recent sales trends
        sales_trends = await SalesService.get_sales_trends(db, days=7)
        
        # Get recent agent decisions related to operations
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=20)
        operational_decisions = [
            d for d in recent_decisions 
            if d.decision_type in ["REORDER", "ALERT"]
        ]
        
        # Calculate priority actions
        priority_actions = []
        
        # Critical stock alerts
        for item in out_of_stock_items[:5]:
            priority_actions.append({
                "type": "critical_stock",
                "priority": "urgent",
                "title": f"Out of Stock: {item.name}",
                "description": f"SKU {item.sku} is completely out of stock",
                "item_id": item.id,
                "action_required": "Immediate reorder"
            })
        
        # Low stock warnings
        for item in low_stock_items[:5]:
            if item not in out_of_stock_items:  # Avoid duplicates
                priority_actions.append({
                    "type": "low_stock",
                    "priority": "high",
                    "title": f"Low Stock: {item.name}",
                    "description": f"Only {item.current_stock} units remaining (reorder at {item.reorder_level})",
                    "item_id": item.id,
                    "action_required": "Review and reorder"
                })
        
        # Overdue orders
        overdue_orders = [
            order for order in pending_orders
            if order.expected_delivery_date and order.expected_delivery_date < datetime.utcnow()
        ]
        
        for order in overdue_orders[:3]:
            priority_actions.append({
                "type": "overdue_order",
                "priority": "high",
                "title": f"Overdue Order: {order.order_number}",
                "description": f"Expected delivery was {order.expected_delivery_date.strftime('%Y-%m-%d')}",
                "order_id": order.id,
                "action_required": "Contact vendor"
            })
        
        # Performance metrics
        performance_metrics = {
            "stock_health": {
                "healthy_items": inventory_summary["healthy_stock_items"],
                "attention_needed": inventory_summary["low_stock_items"] + inventory_summary["out_of_stock_items"],
                "health_percentage": (inventory_summary["healthy_stock_items"] / inventory_summary["total_items"] * 100) if inventory_summary["total_items"] > 0 else 0
            },
            "order_fulfillment": {
                "pending_orders": len(pending_orders),
                "overdue_orders": len(overdue_orders),
                "on_time_rate": (len(pending_orders) - len(overdue_orders)) / len(pending_orders) * 100 if pending_orders else 100
            },
            "ai_recommendations": {
                "total_decisions": len(recent_decisions),
                "reorder_recommendations": len([d for d in operational_decisions if d.decision_type == "REORDER"]),
                "active_alerts": len([d for d in operational_decisions if d.decision_type == "ALERT" and not d.is_executed])
            }
        }
        
        return {
            "success": True,
            "dashboard_type": "scm",
            "summary": {
                "total_items": inventory_summary["total_items"],
                "critical_items": len(out_of_stock_items),
                "low_stock_items": len(low_stock_items),
                "pending_orders": len(pending_orders),
                "priority_actions_count": len(priority_actions)
            },
            "priority_actions": priority_actions,
            "performance_metrics": performance_metrics,
            "recent_trends": {
                "sales_trend_7days": sales_trends[-7:] if sales_trends else [],
                "avg_daily_sales": sum(day.get("total_quantity", 0) for day in sales_trends[-7:]) / 7 if sales_trends else 0
            },
            "operational_alerts": [
                {
                    "id": d.id,
                    "type": d.decision_type,
                    "message": d.reasoning,
                    "confidence": d.confidence_score,
                    "created_at": d.created_at.isoformat(),
                    "is_executed": d.is_executed
                }
                for d in operational_decisions[:10]
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get SCM dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SCM dashboard: {str(e)}"
        )


@router.get("/finance", response_model=Dict[str, Any])
async def get_finance_dashboard(db: AsyncSession = Depends(get_db)):
    """
    Finance Officer dashboard
    Focus on costs, budget impact, and financial metrics
    """
    try:
        # Get inventory summary
        inventory_summary = await InventoryService.get_inventory_summary(db)
        
        # Get recent sales data for revenue calculation
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        recent_sales = await SalesService.get_sales_by_period(db, start_date, end_date)
        
        # Get pending orders for cost analysis
        pending_orders = await OrderService.get_pending_orders(db)
        
        # Get recent agent decisions for cost impact
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=50)
        reorder_decisions = [
            d for d in recent_decisions 
            if d.decision_type == "REORDER" and not d.is_executed
        ]
        
        # Calculate financial metrics
        total_revenue_30days = sum(sale.total_amount for sale in recent_sales)
        avg_daily_revenue = total_revenue_30days / 30
        
        # Estimate pending order costs
        pending_order_cost = sum(order.total_amount for order in pending_orders)
        
        # Estimate reorder recommendation costs
        estimated_reorder_cost = 0
        for decision in reorder_decisions:
            try:
                decision_data = eval(decision.decision_data) if decision.decision_data else {}
                estimated_cost = decision_data.get("estimated_cost", 0)
                estimated_reorder_cost += estimated_cost
            except:
                estimated_reorder_cost += 100  # Default estimate
        
        # Calculate inventory value (simplified)
        all_items = await InventoryService.get_all_items(db)
        total_inventory_value = sum(item.current_stock * item.unit_cost for item in all_items)
        
        # Budget alerts
        budget_alerts = []
        
        if estimated_reorder_cost > avg_daily_revenue * 10:  # More than 10 days revenue
            budget_alerts.append({
                "type": "high_reorder_cost",
                "severity": "high",
                "message": f"Pending reorders estimated at ${estimated_reorder_cost:,.2f}",
                "impact": "Significant budget impact"
            })
        
        if pending_order_cost > avg_daily_revenue * 15:
            budget_alerts.append({
                "type": "high_pending_cost",
                "severity": "medium",
                "message": f"Pending orders total ${pending_order_cost:,.2f}",
                "impact": "Review cash flow"
            })
        
        # Cost breakdown by category
        cost_by_category = {}
        for item in all_items:
            category = str(item.category).replace("ItemCategory.", "")
            if category not in cost_by_category:
                cost_by_category[category] = {"value": 0, "items": 0}
            cost_by_category[category]["value"] += item.current_stock * item.unit_cost
            cost_by_category[category]["items"] += 1
        
        # Financial performance metrics
        financial_metrics = {
            "revenue_metrics": {
                "revenue_30days": total_revenue_30days,
                "avg_daily_revenue": avg_daily_revenue,
                "revenue_trend": "stable"  # Could be calculated from trends
            },
            "cost_metrics": {
                "inventory_value": total_inventory_value,
                "pending_orders_cost": pending_order_cost,
                "estimated_reorder_cost": estimated_reorder_cost,
                "total_committed_cost": pending_order_cost + estimated_reorder_cost
            },
            "efficiency_metrics": {
                "inventory_turnover": (total_revenue_30days / total_inventory_value) * 12 if total_inventory_value > 0 else 0,  # Annualized
                "cost_per_transaction": total_inventory_value / len(recent_sales) if recent_sales else 0,
                "avg_order_value": sum(sale.total_amount for sale in recent_sales) / len(recent_sales) if recent_sales else 0
            }
        }
        
        return {
            "success": True,
            "dashboard_type": "finance",
            "summary": {
                "inventory_value": total_inventory_value,
                "monthly_revenue": total_revenue_30days,
                "pending_commitments": pending_order_cost + estimated_reorder_cost,
                "budget_alerts_count": len(budget_alerts)
            },
            "financial_metrics": financial_metrics,
            "budget_alerts": budget_alerts,
            "cost_breakdown": {
                "by_category": cost_by_category,
                "pending_orders": [
                    {
                        "order_number": order.order_number,
                        "vendor_id": order.vendor_id,
                        "amount": order.total_amount,
                        "order_date": order.order_date.isoformat()
                    }
                    for order in pending_orders[:10]
                ],
                "reorder_estimates": [
                    {
                        "decision_id": d.id,
                        "item_id": d.item_id,
                        "estimated_cost": eval(d.decision_data).get("estimated_cost", 0) if d.decision_data else 0,
                        "confidence": d.confidence_score,
                        "created_at": d.created_at.isoformat()
                    }
                    for d in reorder_decisions[:10]
                ]
            },
            "cash_flow_projection": {
                "next_30_days": {
                    "expected_revenue": avg_daily_revenue * 30,
                    "committed_costs": pending_order_cost + estimated_reorder_cost,
                    "net_projection": (avg_daily_revenue * 30) - (pending_order_cost + estimated_reorder_cost)
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get finance dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get finance dashboard: {str(e)}"
        )


@router.get("/overview", response_model=Dict[str, Any])
async def get_overview_dashboard(db: AsyncSession = Depends(get_db)):
    """
    General overview dashboard
    High-level metrics for all users
    """
    try:
        # Get basic metrics
        inventory_summary = await InventoryService.get_inventory_summary(db)
        
        # Get recent activity
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        recent_sales = await SalesService.get_sales_by_period(db, start_date, end_date)
        top_items = await SalesService.get_top_selling_items(db, limit=5, days=7)
        
        # Get system activity
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=10)
        pending_orders = await OrderService.get_pending_orders(db)
        
        # Get vendors
        vendors = await VendorService.get_all_vendors(db)
        
        # Calculate key metrics
        total_sales_7days = sum(sale.total_amount for sale in recent_sales)
        total_transactions_7days = len(recent_sales)
        
        # System health indicators
        health_indicators = {
            "inventory_health": "good" if inventory_summary["out_of_stock_items"] == 0 else "needs_attention",
            "sales_activity": "active" if total_transactions_7days > 0 else "low",
            "ai_agent_status": "active" if recent_decisions else "inactive",
            "vendor_network": "healthy" if len(vendors) >= 3 else "limited"
        }
        
        return {
            "success": True,
            "dashboard_type": "overview",
            "summary": {
                "total_items": inventory_summary["total_items"],
                "healthy_stock": inventory_summary["healthy_stock_items"],
                "items_needing_attention": inventory_summary["low_stock_items"] + inventory_summary["out_of_stock_items"],
                "active_vendors": len(vendors),
                "pending_orders": len(pending_orders),
                "weekly_sales": total_sales_7days,
                "weekly_transactions": total_transactions_7days
            },
            "health_indicators": health_indicators,
            "key_metrics": {
                "inventory_status": {
                    "total": inventory_summary["total_items"],
                    "healthy": inventory_summary["healthy_stock_items"],
                    "low_stock": inventory_summary["low_stock_items"],
                    "out_of_stock": inventory_summary["out_of_stock_items"]
                },
                "recent_performance": {
                    "sales_7days": total_sales_7days,
                    "transactions_7days": total_transactions_7days,
                    "avg_transaction_value": total_sales_7days / total_transactions_7days if total_transactions_7days > 0 else 0
                }
            },
            "recent_activity": {
                "top_selling_items": [
                    {
                        "name": item.get("name", "Unknown"),
                        "sku": item.get("sku", "Unknown"),
                        "total_sold": item.get("total_sold", 0),
                        "revenue": item.get("total_revenue", 0)
                    }
                    for item in top_items
                ],
                "recent_decisions": [
                    {
                        "type": d.decision_type,
                        "summary": d.reasoning[:100] + "..." if len(d.reasoning) > 100 else d.reasoning,
                        "confidence": d.confidence_score,
                        "created_at": d.created_at.isoformat()
                    }
                    for d in recent_decisions[:5]
                ]
            },
            "alerts_summary": {
                "critical": inventory_summary["out_of_stock_items"],
                "warnings": inventory_summary["low_stock_items"],
                "ai_recommendations": len([d for d in recent_decisions if not d.is_executed])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get overview dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get overview dashboard: {str(e)}"
        )


@router.get("/quick-stats")
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    """Get quick statistics for dashboard widgets"""
    try:
        # Get inventory counts
        inventory_summary = await InventoryService.get_inventory_summary(db)
        
        # Get today's sales
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_sales = await SalesService.get_sales_by_period(
            db, today_start, datetime.utcnow()
        )
        
        # Get pending orders count
        pending_orders = await OrderService.get_pending_orders(db)
        
        # Get recent AI activity
        recent_decisions = await AgentDecisionService.get_recent_decisions(db, limit=5)
        
        return {
            "success": True,
            "quick_stats": {
                "inventory": {
                    "total_items": inventory_summary["total_items"],
                    "low_stock": inventory_summary["low_stock_items"],
                    "out_of_stock": inventory_summary["out_of_stock_items"]
                },
                "sales_today": {
                    "transactions": len(today_sales),
                    "revenue": sum(sale.total_amount for sale in today_sales),
                    "units_sold": sum(sale.quantity_sold for sale in today_sales)
                },
                "orders": {
                    "pending": len(pending_orders),
                    "total_value": sum(order.total_amount for order in pending_orders)
                },
                "ai_activity": {
                    "recent_decisions": len(recent_decisions),
                    "last_analysis": recent_decisions[0].created_at.isoformat() if recent_decisions else None
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get quick stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quick stats: {str(e)}"
        )