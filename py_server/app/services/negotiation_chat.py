"""
AI-Powered Supplier Negotiation Chat System
Simulates real-time negotiations with suppliers using AI agents.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random
import json
from uuid import uuid4
import logging

from app.services.ai_service import get_ai_service, VeriChainAIService
from app.services.notifications_enhanced import notification_manager

logger = logging.getLogger(__name__)

class MessageType(Enum):
    SYSTEM = "system"
    USER = "user"
    SUPPLIER = "supplier"
    AI_AGENT = "ai_agent"

class NegotiationPhase(Enum):
    INITIAL_INQUIRY = "initial_inquiry"
    PRICE_DISCUSSION = "price_discussion"
    TERMS_NEGOTIATION = "terms_negotiation"
    FINAL_AGREEMENT = "final_agreement"
    CONCLUDED = "concluded"

@dataclass
class ChatMessage:
    id: str
    sender: str
    sender_type: MessageType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "sender_type": self.sender_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }

@dataclass
class NegotiationSession:
    session_id: str
    item_sku: str
    item_name: str
    supplier_name: str
    supplier_email: str
    initial_price: float
    target_price: float
    current_offer: Optional[float]
    phase: NegotiationPhase
    messages: List[ChatMessage]
    metadata: Dict[str, Any]
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    
    def add_message(self, sender: str, sender_type: MessageType, content: str, metadata: Dict = None):
        message = ChatMessage(
            id=str(uuid4()),
            sender=sender,
            sender_type=sender_type,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        self.messages.append(message)
        self.last_activity = datetime.utcnow()
        return message

class SupplierPersonality:
    """Simulates different supplier personalities for realistic negotiations."""
    
    AGGRESSIVE = {
        "name": "Aggressive",
        "description": "Firm on prices, minimal discounts",
        "price_flexibility": 0.03,  # 3% max discount
        "response_style": "direct",
        "negotiation_rounds": 2,
        "common_phrases": [
            "This is our best price",
            "We cannot go lower than this",
            "Take it or leave it",
            "Market rates don't allow further reduction"
        ]
    }
    
    COOPERATIVE = {
        "name": "Cooperative", 
        "description": "Willing to negotiate, values relationships",
        "price_flexibility": 0.12,  # 12% max discount
        "response_style": "friendly",
        "negotiation_rounds": 4,
        "common_phrases": [
            "Let's find a win-win solution",
            "We value long-term partnerships",
            "How can we make this work for both of us?",
            "We're flexible on terms"
        ]
    }
    
    STRATEGIC = {
        "name": "Strategic",
        "description": "Data-driven, considers volume and terms",
        "price_flexibility": 0.08,  # 8% max discount
        "response_style": "analytical",
        "negotiation_rounds": 3,
        "common_phrases": [
            "Based on market analysis...",
            "Considering the volume commitment...",
            "Our pricing model shows...",
            "Let's look at the total value proposition"
        ]
    }

class SupplierNegotiationChat:
    """AI-powered supplier negotiation chat system."""
    
    def __init__(self, ai_service: VeriChainAIService = None):
        self.ai_service = ai_service
        self.active_sessions: Dict[str, NegotiationSession] = {}
        self.supplier_personalities = [
            SupplierPersonality.AGGRESSIVE,
            SupplierPersonality.COOPERATIVE,
            SupplierPersonality.STRATEGIC
        ]
        
        # Mock supplier database
        self.suppliers = {
            "rajesh_stationery": {
                "name": "Rajesh Kumar",
                "company": "Rajesh Stationery Wholesale",
                "email": "rajesh@rswholesale.com",
                "personality": SupplierPersonality.COOPERATIVE,
                "specialties": ["WRITING_INSTRUMENTS", "PAPER_NOTEBOOKS"],
                "response_delay": (2, 8),  # 2-8 minutes response time
                "availability": "9am-6pm IST"
            },
            "modern_office": {
                "name": "Priya Sharma",
                "company": "Modern Office Solutions",
                "email": "priya@modernofficeindia.com", 
                "personality": SupplierPersonality.STRATEGIC,
                "specialties": ["OFFICE_SUPPLIES", "BAGS_STORAGE"],
                "response_delay": (5, 15),  # 5-15 minutes response time
                "availability": "10am-7pm IST"
            },
            "creative_arts": {
                "name": "Amit Patel",
                "company": "Creative Arts Suppliers",
                "email": "amit@creativeartsupply.in",
                "personality": SupplierPersonality.AGGRESSIVE,
                "specialties": ["ART_CRAFT"],
                "response_delay": (10, 30),  # 10-30 minutes response time
                "availability": "9am-5pm IST"
            }
        }
    
    async def start_negotiation(self, item_sku: str, item_name: str, 
                              initial_price: float, target_price: float,
                              supplier_id: str, quantity: int = 100) -> str:
        """Start a new negotiation session with a supplier."""
        
        if supplier_id not in self.suppliers:
            raise ValueError(f"Supplier {supplier_id} not found")
        
        supplier = self.suppliers[supplier_id]
        session_id = f"neg_{item_sku}_{supplier_id}_{int(datetime.now().timestamp())}"
        
        # Create negotiation session
        session = NegotiationSession(
            session_id=session_id,
            item_sku=item_sku,
            item_name=item_name,
            supplier_name=supplier["company"],
            supplier_email=supplier["email"],
            initial_price=initial_price,
            target_price=target_price,
            current_offer=initial_price,
            phase=NegotiationPhase.INITIAL_INQUIRY,
            messages=[],
            metadata={
                "supplier_id": supplier_id,
                "supplier_contact": supplier["name"],
                "quantity": quantity,
                "personality": supplier["personality"]["name"],
                "max_discount": supplier["personality"]["price_flexibility"]
            },
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Add system message
        session.add_message(
            sender="System",
            sender_type=MessageType.SYSTEM,
            content=f"Negotiation started for {item_name} with {supplier['company']}. Initial quote: ₹{initial_price:.2f}, Target: ₹{target_price:.2f}",
            metadata={"action": "session_started"}
        )
        
        # Send initial inquiry
        await self._send_initial_inquiry(session)
        
        # Store session
        self.active_sessions[session_id] = session
        
        print(f"🤝 Started negotiation {session_id} with {supplier['company']}")
        return session_id
    
    async def _send_initial_inquiry(self, session: NegotiationSession):
        """Send initial inquiry message."""
        
        supplier = self.suppliers[session.metadata["supplier_id"]]
        
        # AI-generated initial message
        initial_message = await self._generate_ai_message(
            session, 
            f"Generate a professional initial inquiry for {session.item_name} ({session.metadata['quantity']} units). Current quote is ₹{session.initial_price:.2f}. Be polite but indicate we're looking for better pricing."
        )
        
        # Add our message
        session.add_message(
            sender="VeriChain Procurement",
            sender_type=MessageType.USER,
            content=initial_message,
            metadata={"phase": "initial_inquiry"}
        )
        
        # Simulate supplier response
        await asyncio.sleep(2)  # Simulate thinking time
        await self._generate_supplier_response(session)
    
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message in an active negotiation."""
        
        if session_id not in self.active_sessions:
            return {"error": "Negotiation session not found"}
        
        session = self.active_sessions[session_id]
        
        if not session.is_active:
            return {"error": "Negotiation session is closed"}
        
        # Add user message
        user_message = session.add_message(
            sender="VeriChain Procurement",
            sender_type=MessageType.USER,
            content=message
        )
        
        # Analyze message for price offers
        price_offer = self._extract_price_from_message(message)
        if price_offer:
            session.current_offer = price_offer
            session.metadata["last_offer"] = price_offer
        
        # Update negotiation phase
        self._update_negotiation_phase(session)
        
        # Schedule supplier response (simulate delay)
        supplier = self.suppliers[session.metadata["supplier_id"]]
        delay_range = supplier["response_delay"]
        response_delay = random.uniform(delay_range[0], delay_range[1])
        
        # For demo, reduce delay significantly
        response_delay = min(response_delay, 5)  # Max 5 seconds for demo
        
        asyncio.create_task(
            self._delayed_supplier_response(session, response_delay)
        )
        
        return {
            "message_id": user_message.id,
            "status": "sent",
            "supplier_response_eta": f"{response_delay:.0f} seconds"
        }
    
    async def _delayed_supplier_response(self, session: NegotiationSession, delay: float):
        """Generate delayed supplier response."""
        await asyncio.sleep(delay)
        await self._generate_supplier_response(session)
    
    async def _generate_supplier_response(self, session: NegotiationSession):
        """Generate intelligent supplier response using AI."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        personality = supplier_data["personality"]
        
        # Get AI service
        if not self.ai_service:
            self.ai_service = await get_ai_service()
        
        # Prepare session data for AI
        session_data = {
            "item_sku": session.item_sku,
            "item_name": session.item_name,
            "initial_price": session.initial_price,
            "current_offer": session.current_offer,
            "target_price": session.target_price,
            "quantity": session.metadata.get("quantity", 100),
            "supplier_id": session.metadata["supplier_id"],
            "supplier_name": session.supplier_name
        }
        
        # Get message history for AI context
        message_history = [
            {
                "sender": msg.sender,
                "sender_type": msg.sender_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.messages
        ]
        
        try:
            # Get AI negotiation decision
            negotiation_decision = await self.ai_service.negotiate_with_supplier(
                session_data, message_history, personality
            )
            
            logger.info(f"AI Decision for {session.session_id}: {negotiation_decision.action} - {negotiation_decision.reasoning}")
            
            # Generate supplier response based on AI decision
            supplier_response_text = await self.ai_service.generate_supplier_response(
                negotiation_decision, personality, session_data
            )
            
            # Create response object
            response = {
                "content": supplier_response_text,
                "metadata": {
                    "ai_action": negotiation_decision.action,
                    "ai_confidence": negotiation_decision.confidence,
                    "ai_strategy": negotiation_decision.strategy,
                    "ai_reasoning": negotiation_decision.reasoning
                }
            }
            
            # Handle price updates
            if negotiation_decision.action == "counter" and negotiation_decision.price_offer:
                response["new_price"] = negotiation_decision.price_offer
                session.current_offer = negotiation_decision.price_offer
            elif negotiation_decision.action == "accept":
                response["new_price"] = session.target_price
                session.current_offer = session.target_price
                response["metadata"]["agreement_reached"] = True
            
            # Determine if negotiation should conclude
            if negotiation_decision.action in ["accept", "reject"]:
                session.phase = NegotiationPhase.CONCLUDED
                session.is_active = False
                await self._finalize_negotiation(session, negotiation_decision.action == "accept")
            
        except Exception as e:
            logger.error(f"AI negotiation failed: {e}")
            # Fallback to rule-based response
            context = self._analyze_negotiation_context(session)
            response_strategy = self._determine_response_strategy(session, context)
            
            if response_strategy["type"] == "price_counter":
                response = await self._generate_price_counter_response(session, response_strategy)
            elif response_strategy["type"] == "accept":
                response = await self._generate_acceptance_response(session, response_strategy)
            elif response_strategy["type"] == "reject":
                response = await self._generate_rejection_response(session, response_strategy)
            else:
                response = await self._generate_general_response(session, response_strategy)
        
        # Initialize response_strategy if not set (for successful AI case)
        if 'response_strategy' not in locals():
            response_strategy = {"conclude": False, "agreement": False}
        
        # Add supplier message
        supplier_message = session.add_message(
            sender=supplier_data["name"],
            sender_type=MessageType.SUPPLIER,
            content=response["content"],
            metadata=response.get("metadata", {})
        )
        
        # Update session based on response
        if "new_price" in response:
            session.current_offer = response["new_price"]
        
        # Check if negotiation should conclude
        if response_strategy.get("conclude"):
            session.phase = NegotiationPhase.CONCLUDED
            session.is_active = False
            await self._finalize_negotiation(session, response_strategy.get("agreement", False))
        
        # Notify about new message
        await notification_manager.send_notification(
            type="supplier_response",
            title=f"Response from {supplier_data['company']}",
            message=response["content"][:100] + "...",
            recipient="procurement@verichain.com"
        )
        
        print(f"💬 Supplier response in {session.session_id}: {response['content'][:50]}...")
        
        return supplier_message
    
    def _analyze_negotiation_context(self, session: NegotiationSession) -> Dict[str, Any]:
        """Analyze current negotiation context."""
        
        messages = session.messages
        user_messages = [m for m in messages if m.sender_type == MessageType.USER]
        
        current_offer = session.current_offer or session.initial_price
        target_price = session.target_price
        price_gap = current_offer - target_price
        price_gap_percentage = (price_gap / current_offer) * 100
        
        # Count negotiation rounds
        rounds = len([m for m in messages if m.sender_type in [MessageType.USER, MessageType.SUPPLIER]]) // 2
        
        return {
            "rounds": rounds,
            "price_gap": price_gap,
            "price_gap_percentage": price_gap_percentage,
            "user_message_count": len(user_messages),
            "last_user_message": user_messages[-1].content if user_messages else "",
            "negotiation_duration": (datetime.utcnow() - session.created_at).total_seconds() / 60
        }
    
    def _determine_response_strategy(self, session: NegotiationSession, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine supplier's response strategy based on personality and context."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        personality = supplier_data["personality"]
        
        current_offer = session.current_offer or session.initial_price
        max_discount = personality["price_flexibility"]
        minimum_price = session.initial_price * (1 - max_discount)
        
        rounds = context["rounds"]
        max_rounds = personality["negotiation_rounds"]
        
        # Check if we've reached supplier's bottom line
        if session.target_price < minimum_price:
            if rounds >= max_rounds:
                return {"type": "reject", "reason": "below_minimum", "conclude": True}
            else:
                return {"type": "counter_with_justification", "final_warning": True}
        
        # Check if target price is acceptable
        if session.target_price >= minimum_price and context["price_gap_percentage"] <= 2:
            return {"type": "accept", "conclude": True, "agreement": True}
        
        # Generate counter-offer
        if rounds < max_rounds:
            # Calculate counter-offer price
            remaining_flexibility = max_discount * (1 - rounds / max_rounds)
            counter_price = session.initial_price * (1 - remaining_flexibility)
            counter_price = max(counter_price, minimum_price)
            
            return {
                "type": "price_counter",
                "new_price": counter_price,
                "justification": self._get_justification_reason(personality, context)
            }
        else:
            # Final round
            return {
                "type": "final_offer",
                "new_price": minimum_price,
                "conclude": True if context["price_gap_percentage"] > 5 else False
            }
    
    def _get_justification_reason(self, personality: Dict, context: Dict) -> str:
        """Get justification reason based on personality."""
        
        reasons = {
            "Aggressive": [
                "material_costs",
                "market_rates", 
                "minimum_margin",
                "no_flexibility"
            ],
            "Cooperative": [
                "partnership_value",
                "volume_consideration",
                "mutual_benefit",
                "long_term_relationship"
            ],
            "Strategic": [
                "cost_analysis",
                "market_comparison",
                "value_proposition",
                "roi_calculation"
            ]
        }
        
        return random.choice(reasons.get(personality["name"], reasons["Strategic"]))
    
    async def _generate_price_counter_response(self, session: NegotiationSession, 
                                             strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate price counter-offer response."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        personality = supplier_data["personality"]
        new_price = strategy["new_price"]
        
        # AI-generated response based on personality
        prompt = f"""
        Generate a supplier response for price negotiation:
        
        Context:
        - Supplier: {supplier_data['company']} ({personality['name']} personality)
        - Product: {session.item_name}
        - Previous offer: ₹{session.current_offer:.2f}
        - New counter-offer: ₹{new_price:.2f}
        - Justification: {strategy.get('justification', 'standard_terms')}
        
        Style: {personality['response_style']}
        Phrases to use: {random.choice(personality['common_phrases'])}
        
        Generate a professional response (2-3 sentences) that:
        1. Acknowledges the negotiation
        2. Presents the counter-offer
        3. Provides brief justification
        
        Be realistic and business-like.
        """
        
        try:
            if not self.ai_service:
                self.ai_service = await get_ai_service()
            
            ai_response = await self.ai_service.llm.ainvoke(prompt)
            content = ai_response.content.strip() if hasattr(ai_response, 'content') else str(ai_response).strip()
        except Exception as e:
            logger.error(f"AI generation failed, using fallback: {e}")
            content = f"Thank you for your inquiry. Based on our costs and market conditions, we can offer ₹{new_price:.2f} per unit. This reflects our best pricing considering the current market scenario."
        
        return {
            "content": content,
            "new_price": new_price,
            "metadata": {
                "action": "price_counter",
                "justification": strategy.get("justification")
            }
        }
    
    async def _generate_acceptance_response(self, session: NegotiationSession,
                                          strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acceptance response."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        
        content = f"Excellent! We're pleased to accept your offer of ₹{session.target_price:.2f} per unit for {session.item_name}. We look forward to a successful partnership. Please proceed with the purchase order and we'll ensure timely delivery."
        
        return {
            "content": content,
            "metadata": {
                "action": "accept",
                "final_price": session.target_price,
                "agreement_reached": True
            }
        }
    
    async def _generate_rejection_response(self, session: NegotiationSession,
                                         strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rejection response."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        personality = supplier_data["personality"]
        
        if strategy["reason"] == "below_minimum":
            content = f"I appreciate your interest, but ₹{session.target_price:.2f} is below our cost price. Our minimum viable price is ₹{session.initial_price * (1 - personality['price_flexibility']):.2f}. We hope you understand our position."
        else:
            content = f"Thank you for the negotiation opportunity. Unfortunately, we cannot meet your target price at this time. Please feel free to reach out in the future if your requirements change."
        
        return {
            "content": content,
            "metadata": {
                "action": "reject",
                "reason": strategy["reason"]
            }
        }
    
    async def _generate_general_response(self, session: NegotiationSession,
                                       strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general response for other scenarios."""
        
        supplier_data = self.suppliers[session.metadata["supplier_id"]]
        
        content = "Thank you for your message. Let me review your requirements and get back to you with our best offer. We value your business and want to find a mutually beneficial solution."
        
        return {
            "content": content,
            "metadata": {"action": "general_response"}
        }
    
    def _extract_price_from_message(self, message: str) -> Optional[float]:
        """Extract price offer from user message."""
        import re
        
        # Look for price patterns
        price_patterns = [
            r'₹\s*(\d+(?:\.\d{2})?)',  # ₹100.50
            r'Rs\.?\s*(\d+(?:\.\d{2})?)',  # Rs. 100.50
            r'(\d+(?:\.\d{2})?)\s*rupees?',  # 100.50 rupees
            r'offer\s+₹?\s*(\d+(?:\.\d{2})?)',  # offer ₹100
            r'price\s+₹?\s*(\d+(?:\.\d{2})?)',  # price ₹100
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _update_negotiation_phase(self, session: NegotiationSession):
        """Update negotiation phase based on current state."""
        
        if session.phase == NegotiationPhase.INITIAL_INQUIRY:
            session.phase = NegotiationPhase.PRICE_DISCUSSION
        elif session.phase == NegotiationPhase.PRICE_DISCUSSION:
            if len(session.messages) > 6:  # After several exchanges
                session.phase = NegotiationPhase.TERMS_NEGOTIATION
        elif session.phase == NegotiationPhase.TERMS_NEGOTIATION:
            if len(session.messages) > 10:  # Approaching conclusion
                session.phase = NegotiationPhase.FINAL_AGREEMENT
    
    async def _finalize_negotiation(self, session: NegotiationSession, agreement_reached: bool):
        """Finalize negotiation and update records."""
        
        if agreement_reached:
            session.add_message(
                sender="System",
                sender_type=MessageType.SYSTEM,
                content=f"✅ Agreement reached! Final price: ₹{session.current_offer:.2f}. Savings: ₹{session.initial_price - session.current_offer:.2f}",
                metadata={
                    "action": "agreement_reached",
                    "final_price": session.current_offer,
                    "savings": session.initial_price - session.current_offer
                }
            )
            
            # Send success notification
            await notification_manager.send_notification(
                type="negotiation_success",
                title="Negotiation Successful!",
                message=f"Agreement reached for {session.item_name} at ₹{session.current_offer:.2f}",
                recipient="procurement@verichain.com"
            )
        else:
            session.add_message(
                sender="System",
                sender_type=MessageType.SYSTEM,
                content="❌ Negotiation concluded without agreement. Consider alternative suppliers or adjust target price.",
                metadata={"action": "negotiation_failed"}
            )
        
        print(f"🏁 Negotiation {session.session_id} concluded: {'Success' if agreement_reached else 'Failed'}")
    
    async def _generate_ai_message(self, session: NegotiationSession, prompt: str) -> str:
        """Generate AI message for negotiation."""
        
        try:
            if not self.ai_service:
                self.ai_service = await get_ai_service()
            
            # Use AI service for message generation
            response = await self.ai_service.llm.ainvoke(prompt)
            return response.content.strip() if hasattr(response, 'content') else str(response).strip()
        except Exception as e:
            logger.error(f"AI message generation failed: {e}")
            return "Thank you for your quote. We're reviewing the pricing and will get back to you with our requirements."
    
    # API Methods for Frontend Integration
    
    async def get_active_negotiations(self) -> List[Dict[str, Any]]:
        """Get all active negotiation sessions."""
        
        active_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_active:
                last_message = session.messages[-1] if session.messages else None
                
                active_sessions.append({
                    "session_id": session_id,
                    "item_name": session.item_name,
                    "supplier_name": session.supplier_name,
                    "initial_price": session.initial_price,
                    "current_offer": session.current_offer,
                    "target_price": session.target_price,
                    "phase": session.phase.value,
                    "message_count": len(session.messages),
                    "last_activity": session.last_activity.isoformat(),
                    "last_message": last_message.content[:50] + "..." if last_message else None,
                    "estimated_savings": session.initial_price - (session.current_offer or session.initial_price)
                })
        
        return sorted(active_sessions, key=lambda x: x["last_activity"], reverse=True)
    
    async def get_negotiation_chat(self, session_id: str) -> Dict[str, Any]:
        """Get complete chat history for a negotiation."""
        
        if session_id not in self.active_sessions:
            return {"error": "Negotiation session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "item_name": session.item_name,
            "supplier_name": session.supplier_name,
            "supplier_contact": session.metadata.get("supplier_contact"),
            "phase": session.phase.value,
            "is_active": session.is_active,
            "initial_price": session.initial_price,
            "current_offer": session.current_offer,
            "target_price": session.target_price,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "messages": [msg.to_dict() for msg in session.messages],
            "metadata": session.metadata
        }
    
    async def get_negotiation_summary(self) -> Dict[str, Any]:
        """Get summary of all negotiations."""
        
        total_sessions = len(self.active_sessions)
        active_sessions = len([s for s in self.active_sessions.values() if s.is_active])
        
        successful_negotiations = 0
        total_savings = 0
        
        for session in self.active_sessions.values():
            if not session.is_active and session.current_offer:
                if session.current_offer < session.initial_price:
                    successful_negotiations += 1
                    total_savings += session.initial_price - session.current_offer
        
        return {
            "total_negotiations": total_sessions,
            "active_negotiations": active_sessions,
            "successful_negotiations": successful_negotiations,
            "total_savings": total_savings,
            "average_savings_per_negotiation": total_savings / max(successful_negotiations, 1),
            "success_rate": (successful_negotiations / max(total_sessions, 1)) * 100
        }


# Global negotiation chat manager
negotiation_chat_manager = None

async def initialize_negotiation_chat():
    """Initialize the negotiation chat system with AI service."""
    global negotiation_chat_manager
    ai_service = await get_ai_service()
    negotiation_chat_manager = SupplierNegotiationChat(ai_service)
    logger.info("💬 Supplier negotiation chat system initialized with AI")

async def get_negotiation_chat_manager() -> SupplierNegotiationChat:
    """Get the negotiation chat manager instance."""
    if negotiation_chat_manager is None:
        await initialize_negotiation_chat()
    return negotiation_chat_manager