"""
Centralized LangChain Gemini AI Service for VeriChain
Provides intelligent AI responses for all system components.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.database import DatabaseManager
from app.models.database import InventoryItemDB, SalesDataDB, AgentDecisionDB, AlertDB

logger = logging.getLogger(__name__)

class AIDecision(BaseModel):
    """Structured AI decision output."""
    decision: str = Field(description="The main decision or recommendation")
    reasoning: str = Field(description="Detailed reasoning behind the decision")
    confidence_score: float = Field(description="Confidence level (0.0-1.0)", ge=0.0, le=1.0)
    data_points: List[str] = Field(description="Key data points considered")
    next_actions: List[str] = Field(description="Recommended next actions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class NegotiationDecision(BaseModel):
    """AI decision for supplier negotiations."""
    action: str = Field(description="Negotiation action: accept, counter, reject, continue")
    price_offer: Optional[float] = Field(description="Counter-offer price if applicable")
    message: str = Field(description="Message to send to supplier")
    reasoning: str = Field(description="Why this action was chosen")
    confidence: float = Field(description="Confidence in this decision", ge=0.0, le=1.0)
    strategy: str = Field(description="Negotiation strategy being used")

class VeriChainAIService:
    """Centralized AI service using LangChain Gemini for all VeriChain operations."""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize LangChain Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=0.3,  # Balanced creativity and consistency
            google_api_key=self.api_key,
            convert_system_message_to_human=True,
            max_tokens=2048
        )
        
        # Initialize output parsers
        self.decision_parser = PydanticOutputParser(pydantic_object=AIDecision)
        self.negotiation_parser = PydanticOutputParser(pydantic_object=NegotiationDecision)
        
        logger.info("✅ VeriChain AI Service initialized with LangChain Gemini")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from multiple possible sources."""
        return (
            settings.google_api_key or 
            settings.gemini_api_key or 
            os.getenv('GOOGLE_API_KEY') or 
            os.getenv('GEMINI_API_KEY')
        )
    
    async def _get_database_context(self, context_type: str, **kwargs) -> Dict[str, Any]:
        """Get relevant database context for AI decisions."""
        context = {}
        
        try:
            # Connect to database if needed
            await self.db_manager.connect()
            
            if context_type == "inventory_analysis":
                # Get current inventory status from database
                session = self.db_manager.get_session()
                try:
                    # Get all inventory items
                    inventory_items = session.query(InventoryItemDB).filter(
                        InventoryItemDB.current_stock > 0
                    ).all()
                    
                    context["total_items"] = len(inventory_items)
                    context["low_stock_items"] = [
                        {
                            "name": item.name,
                            "current_stock": item.current_stock,
                            "minimum_stock": item.min_stock_threshold,
                            "category": item.category
                        }
                        for item in inventory_items 
                        if item.current_stock <= item.min_stock_threshold
                    ]
                    
                    # Get recent sales trends
                    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                    recent_sales = session.query(SalesDataDB).filter(
                        SalesDataDB.date >= thirty_days_ago
                    ).all()
                    
                    context["recent_sales_count"] = len(recent_sales)
                    context["top_selling_items"] = self._get_top_selling_items(recent_sales)
                    
                finally:
                    session.close()
                    
            elif context_type == "supplier_analysis":
                supplier_id = kwargs.get("supplier_id")
                if supplier_id:
                    # Mock supplier data for now
                    context["supplier"] = {
                        "name": "Sample Supplier",
                        "email": "supplier@example.com",
                        "reliability_score": 0.8,
                        "average_delivery_time": 7
                    }
                    context["order_history"] = 5  # Mock order count
                    
            elif context_type == "negotiation_context":
                item_sku = kwargs.get("item_sku")
                if item_sku:
                    session = self.db_manager.get_session()
                    try:
                        # Get item details
                        item = session.query(InventoryItemDB).filter(
                            InventoryItemDB.sku == item_sku
                        ).first()
                        
                        if item:
                            context["item"] = {
                                "name": item.name,
                                "category": item.category,
                                "current_stock": item.current_stock,
                                "minimum_stock": item.min_stock_threshold,
                                "maximum_stock": item.max_stock_capacity,
                                "unit_cost": float(item.unit_cost),
                                "selling_price": float(item.unit_cost * 1.3)  # Mock markup
                            }
                            
                            # Get sales velocity (mock for now)
                            context["sales_velocity"] = self._calculate_mock_sales_velocity()
                    finally:
                        session.close()
            
            return context
            
        except Exception as e:
            logger.error(f"Database context error: {e}")
            return {"error": str(e), "context_type": context_type}
    
    def _get_top_selling_items(self, sales: List) -> List[Dict[str, Any]]:
        """Calculate top selling items from sales data."""
        if not sales:
            return []
            
        item_sales = {}
        for sale in sales:
            sku = sale.sku
            if sku not in item_sales:
                item_sales[sku] = {
                    "quantity": 0,
                    "revenue": 0
                }
            item_sales[sku]["quantity"] += sale.quantity_sold
            item_sales[sku]["revenue"] += float(sale.revenue)
        
        # Sort by quantity sold
        sorted_items = sorted(item_sales.items(), key=lambda x: x[1]["quantity"], reverse=True)
        return [{"item_sku": k, **v} for k, v in sorted_items[:5]]
    
    def _calculate_mock_sales_velocity(self) -> Dict[str, float]:
        """Calculate mock sales velocity metrics."""
        return {
            "daily_average": 5.2,
            "weekly_average": 36.4,
            "trend": "stable"
        }
    
    def _calculate_sales_velocity(self, sales: List) -> Dict[str, float]:
        """Calculate sales velocity metrics."""
        if not sales:
            return {"daily_average": 0, "weekly_average": 0, "trend": "stable"}
        
        # Group sales by week
        weekly_sales = {}
        for sale in sales:
            week = sale.sale_date.isocalendar()[1]
            if week not in weekly_sales:
                weekly_sales[week] = 0
            weekly_sales[week] += sale.quantity
        
        if len(weekly_sales) < 2:
            return {"daily_average": 0, "weekly_average": 0, "trend": "insufficient_data"}
        
        weekly_values = list(weekly_sales.values())
        daily_average = sum(weekly_values) / (len(weekly_values) * 7)
        weekly_average = sum(weekly_values) / len(weekly_values)
        
        # Calculate trend
        if len(weekly_values) >= 2:
            recent_avg = sum(weekly_values[-2:]) / 2
            older_avg = sum(weekly_values[:-2]) / max(len(weekly_values) - 2, 1)
            trend = "increasing" if recent_avg > older_avg * 1.1 else "decreasing" if recent_avg < older_avg * 0.9 else "stable"
        else:
            trend = "stable"
        
        return {
            "daily_average": daily_average,
            "weekly_average": weekly_average,
            "trend": trend
        }
    
    async def analyze_inventory_status(self, context: Dict[str, Any] = None) -> AIDecision:
        """AI analysis of current inventory status with database context."""
        
        # Get database context
        db_context = await self._get_database_context("inventory_analysis")
        
        prompt = f"""
        As a VeriChain AI inventory analyst, analyze the current inventory status and provide actionable insights.
        
        Current Inventory Data:
        - Total items in inventory: {db_context.get('total_items', 0)}
        - Low stock items: {len(db_context.get('low_stock_items', []))}
        - Recent sales (30 days): {db_context.get('recent_sales_count', 0)}
        
        Low Stock Items Details:
        {json.dumps(db_context.get('low_stock_items', []), indent=2)}
        
        Top Selling Items:
        {json.dumps(db_context.get('top_selling_items', []), indent=2)}
        
        Additional Context: {json.dumps(context or {}, indent=2)}
        
        Provide a comprehensive analysis including:
        1. Current inventory health assessment
        2. Urgent action items for low stock
        3. Seasonal trends and predictions
        4. Cost optimization opportunities
        5. Risk assessment and mitigation strategies
        
        {self.decision_parser.get_format_instructions()}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return self.decision_parser.parse(response.content)
        except Exception as e:
            logger.error(f"AI inventory analysis failed: {e}")
            return AIDecision(
                decision="Manual review required",
                reasoning=f"AI analysis failed: {str(e)}",
                confidence_score=0.0,
                data_points=["System error occurred"],
                next_actions=["Review system logs", "Retry analysis"]
            )
    
    async def negotiate_with_supplier(self, session_data: Dict[str, Any], message_history: List[Dict], 
                                    supplier_personality: Dict[str, Any]) -> NegotiationDecision:
        """AI-powered supplier negotiation with real decision making."""
        
        # Get negotiation context from database
        db_context = await self._get_database_context(
            "negotiation_context", 
            item_sku=session_data.get("item_sku"),
            supplier_id=session_data.get("supplier_id")
        )
        
        # Get supplier context
        supplier_context = await self._get_database_context(
            "supplier_analysis",
            supplier_id=session_data.get("supplier_id")
        )
        
        current_offer = session_data.get("current_offer", session_data.get("initial_price"))
        target_price = session_data.get("target_price")
        initial_price = session_data.get("initial_price")
        quantity = session_data.get("quantity", 100)
        
        # Calculate negotiation metrics
        savings_potential = initial_price - target_price
        current_savings = initial_price - current_offer
        savings_percentage = (current_savings / initial_price) * 100 if initial_price > 0 else 0
        
        # Analyze conversation history
        conversation_summary = self._summarize_conversation(message_history)
        negotiation_rounds = len([m for m in message_history if m.get("sender_type") in ["user", "supplier"]]) // 2
        
        prompt = f"""
        As a VeriChain AI negotiation expert, analyze this supplier negotiation and make the best strategic decision.
        
        NEGOTIATION CONTEXT:
        - Item: {session_data.get('item_name')} (SKU: {session_data.get('item_sku')})
        - Quantity: {quantity} units
        - Initial Price: ₹{initial_price:.2f}
        - Current Offer: ₹{current_offer:.2f}
        - Target Price: ₹{target_price:.2f}
        - Current Savings: ₹{current_savings:.2f} ({savings_percentage:.1f}%)
        - Negotiation Round: {negotiation_rounds}
        
        ITEM DATA FROM DATABASE:
        {json.dumps(db_context.get('item', {}), indent=2)}
        
        SUPPLIER PROFILE:
        - Personality: {supplier_personality.get('name')} - {supplier_personality.get('description')}
        - Price Flexibility: {supplier_personality.get('price_flexibility', 0) * 100:.0f}%
        - Max Rounds: {supplier_personality.get('negotiation_rounds', 3)}
        - Response Style: {supplier_personality.get('response_style')}
        
        SUPPLIER DATABASE INFO:
        {json.dumps(supplier_context.get('supplier', {}), indent=2)}
        
        SALES VELOCITY DATA:
        {json.dumps(db_context.get('sales_velocity', {}), indent=2)}
        
        CONVERSATION HISTORY:
        {conversation_summary}
        
        STRATEGIC ANALYSIS REQUIRED:
        1. Assess if current offer is acceptable based on:
           - Market data and cost analysis
           - Supplier's historical performance
           - Item urgency and sales velocity
           - Our profit margins and cost structure
        
        2. Determine optimal negotiation strategy:
           - Should we accept current offer?
           - Make a counter-offer? (calculate optimal price)
           - Continue negotiating with different approach?
           - Consider alternative suppliers?
        
        3. Consider business factors:
           - Long-term supplier relationship value
           - Inventory urgency and carrying costs
           - Seasonal demand patterns
           - Bulk purchase advantages
        
        DECISION ACTIONS:
        - "accept": Accept current offer (explain why it's optimal)
        - "counter": Make strategic counter-offer (provide specific price and reasoning)
        - "continue": Continue negotiating with new approach
        - "reject": End negotiation and seek alternatives
        
        Provide your decision with detailed business reasoning and optimal pricing strategy.
        
        {self.negotiation_parser.get_format_instructions()}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            decision = self.negotiation_parser.parse(response.content)
            
            # Validate decision
            if decision.action == "counter" and decision.price_offer:
                # Ensure counter-offer is realistic
                min_acceptable = target_price * 0.95  # 5% buffer
                max_acceptable = current_offer * 0.98  # Small reduction from current
                
                if decision.price_offer < min_acceptable:
                    decision.price_offer = min_acceptable
                    decision.message += f" (Adjusted to minimum acceptable: ₹{min_acceptable:.2f})"
                elif decision.price_offer > max_acceptable:
                    decision.price_offer = max_acceptable
                    decision.message += f" (Adjusted to maximum viable: ₹{max_acceptable:.2f})"
            
            return decision
            
        except Exception as e:
            logger.error(f"AI negotiation decision failed: {e}")
            # Fallback decision logic
            if current_offer <= target_price * 1.05:  # Within 5% of target
                return NegotiationDecision(
                    action="accept",
                    price_offer=current_offer,
                    message="After careful consideration, we accept your offer. Let's proceed with the order.",
                    reasoning=f"Current offer ₹{current_offer:.2f} is within acceptable range (fallback logic)",
                    confidence=0.7,
                    strategy="pragmatic_acceptance"
                )
            else:
                counter_price = (current_offer + target_price) / 2
                return NegotiationDecision(
                    action="counter",
                    price_offer=counter_price,
                    message=f"We appreciate your offer. Based on market conditions, we'd like to propose ₹{counter_price:.2f} per unit.",
                    reasoning="Fallback counter-offer strategy",
                    confidence=0.6,
                    strategy="middle_ground"
                )
    
    def _summarize_conversation(self, message_history: List[Dict]) -> str:
        """Summarize conversation history for AI context."""
        if not message_history:
            return "No previous conversation"
        
        summary_parts = []
        for msg in message_history[-6:]:  # Last 6 messages
            sender = msg.get("sender", "Unknown")
            content = msg.get("content", "")[:100]  # Truncate long messages
            summary_parts.append(f"{sender}: {content}")
        
        return "\n".join(summary_parts)
    
    async def generate_supplier_response(self, negotiation_decision: NegotiationDecision, 
                                       supplier_personality: Dict[str, Any],
                                       session_context: Dict[str, Any]) -> str:
        """Generate intelligent supplier response based on AI decision."""
        
        prompt = f"""
        As a {supplier_personality.get('name')} supplier named {session_context.get('supplier_name', 'Supplier')}, 
        respond to this negotiation message professionally.
        
        SUPPLIER PERSONALITY:
        - Style: {supplier_personality.get('response_style', 'professional')}
        - Flexibility: {supplier_personality.get('price_flexibility', 0) * 100:.0f}% max discount
        - Common phrases: {', '.join(supplier_personality.get('common_phrases', []))}
        
        NEGOTIATION CONTEXT:
        - Product: {session_context.get('item_name')}
        - Buyer's action: {negotiation_decision.action}
        - Buyer's message: {negotiation_decision.message}
        - Proposed price: ₹{negotiation_decision.price_offer or 0:.2f}
        - Current offer: ₹{session_context.get('current_offer', 0):.2f}
        
        RESPONSE REQUIREMENTS:
        1. Stay in character as this supplier personality
        2. Respond appropriately to the buyer's action
        3. If they made a counter-offer, consider it realistically
        4. Keep response professional and business-appropriate
        5. Length: 2-3 sentences maximum
        
        Generate only the supplier's response message (no extra formatting):
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Supplier response generation failed: {e}")
            # Fallback response
            if negotiation_decision.action == "accept":
                return f"Excellent! We're pleased to confirm your order at ₹{negotiation_decision.price_offer:.2f} per unit. We'll prepare the shipment immediately."
            elif negotiation_decision.action == "counter":
                return f"Thank you for your proposal. Let me review ₹{negotiation_decision.price_offer:.2f} with my team and get back to you shortly."
            else:
                return "Thank you for your interest. We'll consider your proposal and respond accordingly."
    
    async def analyze_auto_ordering_needs(self, context: Dict[str, Any] = None) -> AIDecision:
        """AI analysis for automatic ordering decisions."""
        
        db_context = await self._get_database_context("inventory_analysis")
        
        prompt = f"""
        As a VeriChain AI purchasing agent, analyze inventory data and determine automatic ordering requirements.
        
        CURRENT INVENTORY STATUS:
        {json.dumps(db_context, indent=2)}
        
        ADDITIONAL CONTEXT:
        {json.dumps(context or {}, indent=2)}
        
        ANALYSIS REQUIREMENTS:
        1. Identify items requiring immediate orders (critical stock levels)
        2. Calculate optimal order quantities based on:
           - Sales velocity and trends
           - Seasonal patterns
           - Lead times and carrying costs
           - Economic order quantities
        
        3. Prioritize orders by:
           - Stock urgency (days until stockout)
           - Revenue impact
           - Supplier reliability
           - Cost optimization opportunities
        
        4. Risk assessment:
           - Overstock risks
           - Demand forecasting accuracy
           - Supplier dependency
           - Market price volatility
        
        Provide specific, actionable ordering recommendations with quantities and timing.
        
        {self.decision_parser.get_format_instructions()}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return self.decision_parser.parse(response.content)
        except Exception as e:
            logger.error(f"Auto-ordering analysis failed: {e}")
            return AIDecision(
                decision="Manual review required for ordering",
                reasoning=f"AI analysis failed: {str(e)}",
                confidence_score=0.0,
                data_points=["System error in analysis"],
                next_actions=["Review system", "Manual inventory check"]
            )
    
    async def generate_notification_content(self, notification_type: str, 
                                          context: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligent notification content."""
        
        prompt = f"""
        Generate professional notification content for VeriChain inventory system.
        
        NOTIFICATION TYPE: {notification_type}
        CONTEXT DATA: {json.dumps(context, indent=2)}
        
        Create appropriate content including:
        1. Subject line (concise, actionable)
        2. Email body (professional, informative)  
        3. SMS text (if applicable, under 160 chars)
        4. Dashboard alert (brief summary)
        
        Make content actionable and priority-appropriate.
        
        IMPORTANT: Return ONLY a valid JSON object with these exact keys: 
        subject, email_body, sms_text, dashboard_alert
        
        Example format:
        {{
            "subject": "VeriChain Alert: Low Stock Warning",
            "email_body": "Dear Team, our inventory shows...",
            "sms_text": "VeriChain: Low stock alert",
            "dashboard_alert": "Low stock detected - action required"
        }}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "{" in content and "}" in content:
                # Find the JSON part
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Notification content generation failed: {e}")
            return {
                "subject": f"VeriChain Alert: {notification_type.replace('_', ' ').title()}",
                "email_body": f"System notification: {notification_type.replace('_', ' ')}\nContext: {context}",
                "sms_text": f"VeriChain: {notification_type.replace('_', ' ')}",
                "dashboard_alert": f"{notification_type.replace('_', ' ').title()} - Review required"
            }


# Global AI service instance
ai_service = None

async def get_ai_service() -> VeriChainAIService:
    """Get the global AI service instance."""
    global ai_service
    if ai_service is None:
        ai_service = VeriChainAIService()
    return ai_service

async def initialize_ai_service():
    """Initialize the AI service on startup."""
    global ai_service
    ai_service = VeriChainAIService()
    logger.info("🤖 VeriChain AI Service initialized and ready")