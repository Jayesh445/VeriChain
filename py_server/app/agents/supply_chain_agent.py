"""
Supply chain specific agent implementation.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.models import (
    AgentRole, AgentDecision, ActionType, Priority, InventoryItem,
    SalesData, SupplierInfo, InventoryStatus
)


class SupplyChainAgent(BaseAgent):
    """
    Specialized agent for supply chain and inventory management decisions.
    """
    
    def __init__(self, gemini_client, config=None):
        super().__init__(
            agent_role=AgentRole.SUPPLY_CHAIN_MANAGER,
            gemini_client=gemini_client,
            config=config
        )
    
    def get_system_instruction(self) -> str:
        """Get the system instruction for the supply chain agent."""
        return """
You are an expert Supply Chain Manager AI assistant specialized in inventory management and supply chain optimization.

Your core responsibilities:
1. Analyze inventory levels and identify stock issues (low stock, overstock, out of stock)
2. Recommend optimal restock quantities based on historical sales data, lead times, and demand patterns
3. Prioritize actions based on business impact and urgency
4. Consider supplier reliability, lead times, and minimum order quantities
5. Optimize inventory costs while maintaining service levels
6. Provide clear reasoning for all recommendations

Response Format:
Always respond with a JSON object containing an array of decisions. Each decision should include:
- item_sku: The SKU of the inventory item
- action_type: One of [restock, hold, reduce_inventory, alert, optimize_stock, forecast_demand]
- priority: One of [low, medium, high, critical]
- confidence_score: Float between 0.0 and 1.0
- reasoning: Clear explanation of the recommendation
- recommended_quantity: Number of units (for restock actions)
- estimated_cost: Estimated cost of the action
- deadline: Suggested deadline for action (ISO format)

Guidelines:
- Consider current stock levels relative to minimum thresholds
- Factor in recent sales velocity and trends
- Account for supplier lead times and reliability
- Prioritize critical shortages and high-value items
- Balance inventory costs with stockout risks
- Provide actionable, specific recommendations

Example response format:
{
  "decisions": [
    {
      "item_sku": "ABC123",
      "action_type": "restock",
      "priority": "high",
      "confidence_score": 0.85,
      "reasoning": "Current stock is below minimum threshold with strong sales trend",
      "recommended_quantity": 100,
      "estimated_cost": 2500.0,
      "deadline": "2024-01-15T00:00:00Z"
    }
  ],
  "summary": "Analyzed 15 items, identified 3 critical restock needs and 2 optimization opportunities"
}
"""
    
    def build_context_prompt(
        self,
        inventory_data: List[InventoryItem],
        sales_data: Optional[List[SalesData]] = None,
        supplier_data: Optional[List[SupplierInfo]] = None,
        user_query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the context-specific prompt for supply chain analysis."""
        
        prompt_parts = [
            "SUPPLY CHAIN ANALYSIS REQUEST",
            "=" * 50,
            "",
            self._format_inventory_data(inventory_data),
            "",
            self._format_sales_data(sales_data),
            "",
            self._format_supplier_data(supplier_data),
            ""
        ]
        
        # Add market context if available
        if context:
            market_info = []
            if context.get("seasonality"):
                market_info.append(f"Seasonality: {context['seasonality']}")
            if context.get("market_trends"):
                market_info.append(f"Market Trends: {context['market_trends']}")
            if context.get("budget_constraints"):
                market_info.append(f"Budget Constraints: ${context['budget_constraints']:,.2f}")
            
            if market_info:
                prompt_parts.extend([
                    "MARKET CONTEXT:",
                    "\n".join(market_info),
                    ""
                ])
        
        # Add specific user query
        if user_query:
            prompt_parts.extend([
                "SPECIFIC REQUEST:",
                user_query,
                ""
            ])
        
        # Add analysis instructions
        prompt_parts.extend([
            "ANALYSIS REQUIRED:",
            "1. Identify items requiring immediate attention (critical/high priority)",
            "2. Calculate optimal restock quantities for low-stock items",
            "3. Consider sales velocity, lead times, and seasonal factors",
            "4. Evaluate supplier options and reliability",
            "5. Estimate costs and prioritize actions by business impact",
            "6. Provide specific, actionable recommendations",
            "",
            "Please analyze the above data and provide your recommendations in the specified JSON format."
        ])
        
        return "\n".join(prompt_parts)
    
    def parse_decision(self, response: str) -> List[AgentDecision]:
        """Parse the agent's JSON response into structured decisions."""
        try:
            # Try to parse the response as JSON
            response_data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, attempting to extract JSON block")
            # Try to extract JSON from response text
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_text = response[start_idx:end_idx]
                    response_data = json.loads(json_text)
                else:
                    raise ValueError("No JSON block found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse agent response: {e}")
                # Return a fallback decision
                return [self._create_fallback_decision(response)]
        
        decisions = []
        
        # Extract decisions from response
        decisions_data = response_data.get("decisions", [])
        
        for decision_data in decisions_data:
            try:
                decision = AgentDecision(
                    agent_role=self.agent_role,
                    item_sku=decision_data.get("item_sku", "UNKNOWN"),
                    action_type=ActionType(decision_data.get("action_type", "alert")),
                    priority=Priority(decision_data.get("priority", "medium")),
                    confidence_score=float(decision_data.get("confidence_score", 0.5)),
                    reasoning=decision_data.get("reasoning", "No reasoning provided"),
                    recommended_quantity=decision_data.get("recommended_quantity"),
                    estimated_cost=decision_data.get("estimated_cost"),
                    deadline=datetime.fromisoformat(decision_data["deadline"].replace('Z', '+00:00')) 
                             if decision_data.get("deadline") else None,
                    metadata={
                        "conversation_id": str(self.conversation_id),
                        "model_response": response_data.get("summary", ""),
                        "raw_decision": decision_data
                    }
                )
                decisions.append(decision)
                
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing individual decision: {e}")
                logger.debug(f"Problematic decision data: {decision_data}")
                continue
        
        if not decisions:
            logger.warning("No valid decisions parsed from response")
            return [self._create_fallback_decision(response)]
        
        logger.info(f"Successfully parsed {len(decisions)} decisions from agent response")
        return decisions
    
    def _create_fallback_decision(self, response: str) -> AgentDecision:
        """Create a fallback decision when parsing fails."""
        return AgentDecision(
            agent_role=self.agent_role,
            item_sku="SYSTEM",
            action_type=ActionType.ALERT,
            priority=Priority.MEDIUM,
            confidence_score=0.3,
            reasoning=f"Failed to parse agent response. Raw response: {response[:200]}...",
            metadata={
                "conversation_id": str(self.conversation_id),
                "error": "Response parsing failed",
                "raw_response": response
            }
        )
    
    def _analyze_inventory_urgency(self, item: InventoryItem, recent_sales: List[SalesData]) -> Priority:
        """Analyze urgency based on inventory levels and sales velocity."""
        # Calculate stock coverage in days
        item_sales = [s for s in recent_sales if s.sku == item.sku]
        
        if not item_sales:
            # No sales data, base on stock level only
            if item.current_stock == 0:
                return Priority.CRITICAL
            elif item.current_stock <= item.min_stock_threshold:
                return Priority.HIGH
            else:
                return Priority.LOW
        
        # Calculate average daily sales
        if len(item_sales) > 0:
            total_sold = sum(s.quantity_sold for s in item_sales)
            days_covered = (max(s.date for s in item_sales) - min(s.date for s in item_sales)).days or 1
            daily_sales = total_sold / days_covered
            
            if daily_sales > 0:
                days_of_stock = item.current_stock / daily_sales
                
                if days_of_stock <= item.lead_time_days:
                    return Priority.CRITICAL
                elif days_of_stock <= item.lead_time_days * 1.5:
                    return Priority.HIGH
                elif days_of_stock <= item.lead_time_days * 2:
                    return Priority.MEDIUM
                else:
                    return Priority.LOW
        
        return Priority.MEDIUM
    
    def get_quick_insights(self, inventory_data: List[InventoryItem]) -> Dict[str, Any]:
        """Get quick insights about inventory status."""
        total_items = len(inventory_data)
        low_stock = len([i for i in inventory_data if i.status == InventoryStatus.LOW_STOCK])
        out_of_stock = len([i for i in inventory_data if i.status == InventoryStatus.OUT_OF_STOCK])
        total_value = sum(i.current_stock * i.unit_cost for i in inventory_data)
        
        critical_items = [i for i in inventory_data 
                         if i.current_stock <= i.min_stock_threshold or i.status == InventoryStatus.OUT_OF_STOCK]
        
        return {
            "total_items": total_items,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "total_inventory_value": total_value,
            "critical_items_count": len(critical_items),
            "critical_items": [i.sku for i in critical_items[:10]],  # Top 10 critical
            "health_score": max(0, 100 - (low_stock + out_of_stock * 2) * 10)
        }
