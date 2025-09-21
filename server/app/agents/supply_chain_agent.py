import json
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from langchain.schema import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from app.core.config import settings
from app.core.logging import logger


class SupplyChainAgent:
    """Main AI agent for supply chain decision making"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.agent_model,
            temperature=settings.agent_temperature,
            google_api_key=settings.gemini_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    async def analyze_inventory_situation(
        self, 
        inventory_data: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
        vendor_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze current inventory situation and make recommendations
        """
        try:
            # Prepare structured data for the prompt
            formatted_data = self._format_data_for_analysis(
                inventory_data, sales_data, vendor_data, context
            )
            
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(formatted_data)
            
            # Get AI response
            response = await self._call_gemini_api(prompt)
            
            # Parse and validate response
            parsed_response = self._parse_agent_response(response)
            
            return {
                "success": True,
                "analysis": parsed_response,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": parsed_response.get("confidence_score", 0.8)
            }
            
        except Exception as e:
            logger.error(f"Agent analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _format_data_for_analysis(
        self,
        inventory_data: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
        vendor_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format data for AI analysis"""
        
        # Process inventory data
        inventory_summary = {
            "total_items": len(inventory_data),
            "low_stock_items": [
                item for item in inventory_data 
                if item["current_stock"] <= item["reorder_level"]
            ],
            "out_of_stock_items": [
                item for item in inventory_data 
                if item["current_stock"] <= 0
            ],
            "overstock_items": [
                item for item in inventory_data 
                if item["current_stock"] > item["max_stock_level"] * 1.2
            ],
            "items_by_category": {}
        }
        
        # Group by category
        for item in inventory_data:
            category = item.get("category", "unknown")
            if category not in inventory_summary["items_by_category"]:
                inventory_summary["items_by_category"][category] = []
            inventory_summary["items_by_category"][category].append(item)
        
        # Process sales trends
        sales_summary = {
            "total_transactions": len(sales_data),
            "sales_by_item": {},
            "recent_trends": sales_data[-10:] if sales_data else []  # Last 10 sales
        }
        
        for sale in sales_data:
            item_id = sale.get("item_id")
            if item_id not in sales_summary["sales_by_item"]:
                sales_summary["sales_by_item"][item_id] = {
                    "total_quantity": 0,
                    "total_revenue": 0,
                    "transaction_count": 0
                }
            
            sales_summary["sales_by_item"][item_id]["total_quantity"] += sale.get("quantity_sold", 0)
            sales_summary["sales_by_item"][item_id]["total_revenue"] += sale.get("total_amount", 0)
            sales_summary["sales_by_item"][item_id]["transaction_count"] += 1
        
        # Process vendor data
        vendor_summary = {
            "total_vendors": len(vendor_data),
            "active_vendors": [v for v in vendor_data if v.get("status") == "active"],
            "performance_issues": [
                v for v in vendor_data 
                if v.get("reliability_score", 5) < 6 or v.get("avg_delivery_days", 7) > 10
            ]
        }
        
        return {
            "inventory": inventory_summary,
            "sales": sales_summary,
            "vendors": vendor_summary,
            "context": context or {},
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_analysis_prompt(self, formatted_data: Dict[str, Any]) -> str:
        """Build structured prompt for Gemini API"""
        
        prompt_template = """
You are an autonomous supply chain AI agent specializing in stationery inventory management. 
Analyze the following data and provide actionable recommendations.

CURRENT INVENTORY STATUS:
- Total Items: {total_items}
- Low Stock Items: {low_stock_count} items
- Out of Stock Items: {out_of_stock_count} items
- Overstock Items: {overstock_count} items

LOW STOCK DETAILS:
{low_stock_details}

SALES TRENDS:
- Total Recent Transactions: {total_transactions}
- Top Selling Items: {top_selling_summary}

VENDOR PERFORMANCE:
- Total Active Vendors: {active_vendor_count}
- Performance Issues: {vendor_issues}

ANALYSIS REQUIREMENTS:
1. Identify items requiring immediate reordering (prioritize by business impact)
2. Detect any unusual sales patterns or anomalies
3. Assess vendor performance risks that could affect supply
4. Calculate recommended reorder quantities based on sales velocity
5. Provide risk assessment for potential stockouts in next 30 days

RESPONSE FORMAT (JSON only):
{{
    "restock_recommendations": [
        {{
            "item_id": int,
            "sku": "string",
            "name": "string",
            "current_stock": int,
            "recommended_quantity": int,
            "priority": "high|medium|low",
            "reasoning": "string",
            "estimated_stockout_date": "YYYY-MM-DD"
        }}
    ],
    "anomaly_alerts": [
        {{
            "type": "sales_spike|sales_drop|irregular_pattern",
            "item_id": int,
            "description": "string",
            "severity": "high|medium|low",
            "action_required": "string"
        }}
    ],
    "vendor_risks": [
        {{
            "vendor_id": int,
            "vendor_name": "string",
            "risk_type": "delivery_delay|quality_issue|price_increase",
            "impact": "high|medium|low",
            "mitigation": "string"
        }}
    ],
    "summary": "string - brief executive summary",
    "confidence_score": float,
    "next_analysis_recommended": "YYYY-MM-DD"
}}

Respond ONLY with the JSON object. No explanatory text before or after.
"""
        
        # Format the template with actual data
        inventory = formatted_data["inventory"]
        sales = formatted_data["sales"]
        vendors = formatted_data["vendors"]
        
        # Prepare detailed sections
        low_stock_details = "\n".join([
            f"- {item['sku']}: {item['name']} ({item['current_stock']} units, reorder at {item['reorder_level']})"
            for item in inventory["low_stock_items"][:10]  # Limit to top 10
        ]) or "None"
        
        top_selling_summary = "\n".join([
            f"- Item {item_id}: {data['total_quantity']} units sold"
            for item_id, data in list(sales["sales_by_item"].items())[:5]
        ]) or "No recent sales data"
        
        vendor_issues = "\n".join([
            f"- {v['name']}: Score {v.get('reliability_score', 'N/A')}, Avg delivery {v.get('avg_delivery_days', 'N/A')} days"
            for v in vendors["performance_issues"][:5]
        ]) or "No significant issues"
        
        formatted_prompt = prompt_template.format(
            total_items=inventory["total_items"],
            low_stock_count=len(inventory["low_stock_items"]),
            out_of_stock_count=len(inventory["out_of_stock_items"]),
            overstock_count=len(inventory["overstock_items"]),
            low_stock_details=low_stock_details,
            total_transactions=sales["total_transactions"],
            top_selling_summary=top_selling_summary,
            active_vendor_count=len(vendors["active_vendors"]),
            vendor_issues=vendor_issues
        )
        
        return formatted_prompt
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API directly for analysis"""
        try:
            # Use LangChain's Gemini integration
            response = await self.llm.ainvoke(prompt)
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            # Fallback to direct HTTP call if LangChain fails
            return await self._direct_gemini_call(prompt)
    
    async def _direct_gemini_call(self, prompt: str) -> str:
        """Direct HTTP call to Gemini API as fallback"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.agent_model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": settings.agent_temperature,
                "maxOutputTokens": 2048
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception("No response from Gemini API")
    
    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate agent response"""
        try:
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            parsed = json.loads(cleaned_response)
            
            # Validate required fields
            required_fields = ["restock_recommendations", "anomaly_alerts", "vendor_risks", "summary"]
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = []
            
            # Ensure confidence score
            if "confidence_score" not in parsed:
                parsed["confidence_score"] = 0.75
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response: {str(e)}")
            logger.error(f"Raw response: {response}")
            
            # Return a fallback response
            return {
                "restock_recommendations": [],
                "anomaly_alerts": [{
                    "type": "parsing_error",
                    "description": f"Failed to parse AI response: {str(e)}",
                    "severity": "high",
                    "action_required": "Manual review needed"
                }],
                "vendor_risks": [],
                "summary": "Analysis failed due to response parsing error",
                "confidence_score": 0.1,
                "error": str(e)
            }
    
    async def generate_role_specific_insights(
        self, 
        analysis_result: Dict[str, Any], 
        role: str
    ) -> Dict[str, Any]:
        """Generate role-specific insights from analysis"""
        
        if role.lower() == "scm":  # Supply Chain Manager
            return {
                "operational_alerts": analysis_result.get("restock_recommendations", []),
                "inventory_status": {
                    "critical_items": [
                        item for item in analysis_result.get("restock_recommendations", [])
                        if item.get("priority") == "high"
                    ],
                    "vendor_issues": analysis_result.get("vendor_risks", [])
                },
                "action_items": [
                    f"Review reorder for {len(analysis_result.get('restock_recommendations', []))} items",
                    f"Address {len(analysis_result.get('vendor_risks', []))} vendor risks",
                    "Monitor sales anomalies"
                ]
            }
        
        elif role.lower() == "finance":  # Finance Officer
            restock_cost = sum(
                item.get("recommended_quantity", 0) * 10  # Estimated cost
                for item in analysis_result.get("restock_recommendations", [])
            )
            
            return {
                "financial_impact": {
                    "estimated_reorder_cost": restock_cost,
                    "potential_revenue_at_risk": restock_cost * 2,  # Estimated
                    "vendor_payment_schedule": "TBD"
                },
                "budget_alerts": [
                    item for item in analysis_result.get("restock_recommendations", [])
                    if item.get("priority") == "high"
                ],
                "cost_optimization": {
                    "vendor_negotiations_needed": len(analysis_result.get("vendor_risks", [])),
                    "bulk_order_opportunities": []
                }
            }
        
        else:  # General/Admin view
            return {
                "overview": analysis_result.get("summary", ""),
                "key_metrics": {
                    "items_to_reorder": len(analysis_result.get("restock_recommendations", [])),
                    "anomalies_detected": len(analysis_result.get("anomaly_alerts", [])),
                    "vendor_risks": len(analysis_result.get("vendor_risks", []))
                },
                "recommendations": analysis_result.get("restock_recommendations", [])[:5]
            }


class AgentPromptBuilder:
    """Helper class for building structured prompts"""
    
    @staticmethod
    def build_reorder_prompt(item_data: Dict[str, Any], sales_history: List[Dict[str, Any]]) -> str:
        """Build prompt for reorder decision"""
        return f"""
Analyze reorder requirements for: {item_data['name']} (SKU: {item_data['sku']})

Current Status:
- Stock: {item_data['current_stock']} units
- Reorder Level: {item_data['reorder_level']} units
- Max Stock: {item_data['max_stock_level']} units

Recent Sales (last 7 days): {len(sales_history)} transactions

Recommend:
1. Should we reorder? (yes/no)
2. Recommended quantity
3. Urgency level (high/medium/low)
4. Reasoning

Format: JSON only with fields: reorder, quantity, urgency, reasoning
"""
    
    @staticmethod
    def build_anomaly_detection_prompt(sales_data: List[Dict[str, Any]]) -> str:
        """Build prompt for anomaly detection"""
        return f"""
Analyze sales pattern for anomalies:

Sales Data: {json.dumps(sales_data[-14:], default=str)}  # Last 14 days

Identify:
1. Unusual spikes or drops
2. Pattern changes
3. Seasonal effects
4. Data quality issues

Format: JSON with fields: anomaly_detected, type, severity, description, action_needed
"""