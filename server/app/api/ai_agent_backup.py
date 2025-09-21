"""
AI Agent Negotiation API endpoints for vendor discovery, negotiation, and order approval workflow.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import json
from datetime import datetime, timedelta
import uuid
import random
import asyncio

from app.core.database import get_db
from app.models import StationeryItem, Vendor, Order, AgentDecision, VendorStatus
from app.agents.supply_chain_agent import SupplyChainAgent
from app.core.logging import logger
from pydantic import BaseModel

router = APIRouter()
        "rejected": 100,
        "error": 100
    }
    return progress_map.get(status, 0)


async def _generate_vendor_negotiation_with_gemini(
    session: NegotiationSession, 
    vendor: Vendor, 
    vendor_index: int, 
    total_vendors: int
) -> Dict[str, Any]:
    """Generate realistic vendor negotiation using Gemini AI"""
    
    # Create negotiation context for Gemini
    negotiation_prompt = f"""
You are simulating a vendor negotiation for a supply chain management system. 

NEGOTIATION CONTEXT:
- Item: {session.item_name}
- Quantity Needed: {session.quantity_needed}
- Vendor: {vendor.name}
- Vendor Reliability Score: {vendor.reliability_score}/10
- Average Delivery Days: {vendor.avg_delivery_days}
- Negotiation Number: {vendor_index} of {total_vendors}

Generate a realistic vendor negotiation conversation and proposal. The vendor should:
1. Greet professionally and acknowledge the request
2. Provide a competitive quote based on their reliability and market position
3. Mention any special terms or offers
4. Be realistic about pricing (between $5-30 per unit depending on item complexity)
5. Consider delivery timeframes (3-21 days)

Respond in JSON format:
{{
    "vendor_greeting": "Initial vendor response message",
    "vendor_quote": "Vendor's pricing proposal message",
    "unit_price": 12.50,
    "delivery_days": 7,
    "special_offers": "Optional special offer or null",
    "confidence_score": 0.85,
    "payment_terms": "Net 30 payment terms",
    "additional_notes": "Any additional vendor comments"
}}

Make the negotiation realistic based on the vendor's characteristics.
"""
    
    try:
        # Use Gemini agent for realistic negotiation
        response = await gemini_agent._call_gemini_api(negotiation_prompt)
        
        # Parse Gemini response
        negotiation_data = json.loads(response.strip())
        
        # Create conversation messages
        conversation_messages = [
            ConversationMessage(
                timestamp=datetime.now(),
                speaker=vendor.name,
                message=negotiation_data.get("vendor_greeting", f"Hello! We can supply {session.item_name}. Let me check our pricing..."),
                message_type="negotiation"
            ),
            ConversationMessage(
                timestamp=datetime.now(),
                speaker=vendor.name,
                message=negotiation_data.get("vendor_quote", f"Our quote is ${negotiation_data.get('unit_price', 15.0):.2f}/unit"),
                message_type="proposal"
            ),
            ConversationMessage(
                timestamp=datetime.now(),
                speaker="AI Agent",
                message=f"✅ Received proposal from {vendor.name}. Analyzing terms and market positioning...",
                message_type="negotiation"
            )
        ]
        
        # Add special offers message if present
        if negotiation_data.get("special_offers"):
            conversation_messages.insert(-1, ConversationMessage(
                timestamp=datetime.now(),
                speaker=vendor.name,
                message=f"🎁 Special offer: {negotiation_data['special_offers']}",
                message_type="proposal"
            ))
        
        # Create vendor proposal
        unit_price = float(negotiation_data.get("unit_price", random.uniform(8, 25)))
        delivery_days = int(negotiation_data.get("delivery_days", random.randint(5, 15)))
        confidence_score = float(negotiation_data.get("confidence_score", random.uniform(0.7, 0.95)))
        
        proposal = VendorProposal(
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            unit_price=unit_price,
            total_price=unit_price * session.quantity_needed,
            delivery_time=delivery_days,
            terms=negotiation_data.get("payment_terms", "Net 30 payment terms, FOB destination"),
            confidence_score=confidence_score,
            profit_margin=random.uniform(15, 45),  # Estimated profit margin
            special_offers=negotiation_data.get("special_offers")
        )
        
        return {
            "proposal": proposal,
            "conversation": conversation_messages,
            "gemini_data": negotiation_data
        }
        
    except Exception as e:
        logger.error(f"Gemini negotiation failed for {vendor.name}: {str(e)}")
        # Return fallback data
        return _create_fallback_negotiation_data(vendor, session)


def _create_fallback_proposal(vendor: Vendor, session: NegotiationSession) -> VendorProposal:
    """Create fallback proposal when Gemini fails"""
    base_price = random.uniform(8, 25)
    delivery_days = random.randint(vendor.avg_delivery_days - 2, vendor.avg_delivery_days + 5)
    
    return VendorProposal(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        unit_price=base_price,
        total_price=base_price * session.quantity_needed,
        delivery_time=delivery_days,
        terms="Net 30 payment terms, FOB destination",
        confidence_score=vendor.reliability_score / 10.0,
        profit_margin=random.uniform(20, 40),
        special_offers=None
    )


def _create_fallback_negotiation_data(vendor: Vendor, session: NegotiationSession) -> Dict[str, Any]:
    """Create fallback negotiation data when Gemini fails"""
    proposal = _create_fallback_proposal(vendor, session)
    
    conversation_messages = [
        ConversationMessage(
            timestamp=datetime.now(),
            speaker=vendor.name,
            message=f"Hello! We can supply {session.item_name}. Let me check our current pricing and availability...",
            message_type="negotiation"
        ),
        ConversationMessage(
            timestamp=datetime.now(),
            speaker=vendor.name,
            message=f"💰 Our quote: ${proposal.unit_price:.2f}/unit, {proposal.delivery_time} day delivery. Standard terms apply.",
            message_type="proposal"
        ),
        ConversationMessage(
            timestamp=datetime.now(),
            speaker="AI Agent",
            message=f"✅ Received proposal from {vendor.name}. Processing with backup system...",
            message_type="negotiation"
        )
    ]
    
    return {
        "proposal": proposal,
        "conversation": conversation_messages,
        "gemini_data": None
    }ort logger
from pydantic import BaseModel

router = APIRouter()

# Global storage for negotiation sessions (in production, use database)
negotiation_sessions = {}

# Initialize Gemini agent
gemini_agent = SupplyChainAgent()

# Background negotiation function for auto-refill integration  
async def start_negotiation_background(db: AsyncSession, negotiation_data: dict) -> str:
    """Start AI negotiation process in background for auto-refill"""
    try:
        session_id = str(uuid.uuid4())
        
        # Get item details using async query
        result = await db.execute(select(StationeryItem).filter(StationeryItem.id == negotiation_data["item_id"]))
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError(f"Item {negotiation_data['item_id']} not found")
        
        # Initialize negotiation session
        session = {
            "session_id": session_id,
            "item_id": negotiation_data["item_id"],
            "item_name": item.name,
            "quantity_needed": negotiation_data["quantity_needed"],
            "urgency": negotiation_data["urgency"],
            "status": "discovering",
            "vendor_proposals": [],
            "best_proposal": None,
            "ai_reasoning": f"Auto-refill triggered for {item.name}. Starting vendor discovery...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "trigger_source": negotiation_data.get("trigger_source", "manual"),
            "auto_decision_data": negotiation_data.get("auto_decision_data")
        }
        
        negotiation_sessions[session_id] = session
        
        # Start background processing
        asyncio.create_task(simulate_negotiation_process(session_id, db))
        
        return session_id
        
    except Exception as e:
        raise ValueError(f"Failed to start negotiation: {str(e)}")

async def simulate_negotiation_process(session_id: str, db: AsyncSession):
    """Simulate the complete negotiation process with Gemini AI"""
    try:
        session = negotiation_sessions.get(session_id)
        if not session:
            return
        
        # Phase 1: Vendor Discovery with Gemini AI (2-5 seconds)
        await asyncio.sleep(random.uniform(2, 5))
        session["status"] = "negotiating"
        
        # Use Gemini to analyze the negotiation context
        context_prompt = f"""
        Analyze negotiation strategy for item: {session['item_name']}
        Quantity needed: {session['quantity_needed']}
        Urgency: {session.get('urgency', 'medium')}
        
        Provide a brief reasoning for vendor discovery approach.
        """
        
        try:
            ai_reasoning = await gemini_agent._call_gemini_api(context_prompt)
            session["ai_reasoning"] = f"Gemini AI: {ai_reasoning[:200]}..."
        except Exception as e:
            session["ai_reasoning"] = f"Found 3 potential vendors for {session['item_name']}. Beginning negotiations..."
        
        session["updated_at"] = datetime.now().isoformat()
        
        # Phase 2: Negotiation (5-10 seconds)
        await asyncio.sleep(random.uniform(5, 10))
        session["status"] = "comparing"
        session["ai_reasoning"] = f"Completed negotiations with all vendors. Analyzing proposals..."
        
        # Generate vendor proposals using async query
        result = await db.execute(select(Vendor).limit(3))
        vendors = result.scalars().all()
        base_price = random.uniform(50, 200)
        
        for i, vendor in enumerate(vendors):
            proposal = {
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "unit_price": round(base_price + random.uniform(-10, 20), 2),
                "total_price": round((base_price + random.uniform(-10, 20)) * session["quantity_needed"], 2),
                "delivery_time": random.randint(2, 7),
                "terms": f"Standard terms, {random.choice(['Net 30', 'Net 15', 'COD'])}",
                "confidence_score": random.uniform(0.7, 0.95)
            }
            session["vendor_proposals"].append(proposal)
        
        # Phase 3: Best proposal selection (2 seconds)
        await asyncio.sleep(2)
        session["status"] = "pending_approval"
        session["best_proposal"] = min(session["vendor_proposals"], key=lambda x: x["total_price"])
        session["ai_reasoning"] = f"Best deal found: {session['best_proposal']['vendor_name']} for ${session['best_proposal']['total_price']:.2f}. Awaiting approval..."
        session["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        if session_id in negotiation_sessions:
            negotiation_sessions[session_id]["status"] = "failed"
            negotiation_sessions[session_id]["ai_reasoning"] = f"Negotiation failed: {str(e)}"

# Pydantic models for request/response
class NegotiationRequest(BaseModel):
    item_id: int
    quantity_needed: int
    max_budget: Optional[float] = None
    urgency: str = "medium"  # low, medium, high

class ConversationMessage(BaseModel):
    timestamp: datetime
    speaker: str  # "AI Agent" or "Vendor Name"
    message: str
    message_type: str  # "discovery", "negotiation", "proposal", "counter_offer"

class VendorProposal(BaseModel):
    vendor_id: int
    vendor_name: str
    unit_price: float
    total_price: float
    delivery_time: int  # days
    terms: str
    confidence_score: float
    profit_margin: Optional[float] = None
    special_offers: Optional[str] = None

class NegotiationSession(BaseModel):
    session_id: str
    item_id: int
    item_name: str
    quantity_needed: int
    status: str  # discovering, negotiating, comparing, pending_approval, approved, rejected
    vendor_proposals: List[VendorProposal] = []
    conversation: List[ConversationMessage] = []
    best_proposal: Optional[VendorProposal] = None
    ai_reasoning: str
    created_at: datetime
    updated_at: datetime
    trigger_source: str = "manual"
    
    class Config:
        arbitrary_types_allowed = True

class OrderApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    user_notes: Optional[str] = None

# Global storage for negotiation sessions (in production, use database)
negotiation_sessions = {}

@router.post("/start-negotiation")
async def start_negotiation(
    request: NegotiationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start AI agent negotiation process for an item"""
    try:
        # Get item details using async query
        result = await db.execute(select(StationeryItem).filter(StationeryItem.id == request.item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create negotiation session
        session = NegotiationSession(
            session_id=session_id,
            item_id=request.item_id,
            item_name=item.name,
            quantity_needed=request.quantity_needed,
            status="discovering",
            vendor_proposals=[],
            best_proposal=None,
            ai_reasoning="Starting vendor discovery process...",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        negotiation_sessions[session_id] = session
        
        # Start background negotiation process
        asyncio.create_task(_run_negotiation_process(session_id, db))
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "discovering",
            "message": "AI agent started vendor discovery process",
            "estimated_duration": "2-5 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/negotiation-status/{session_id}")
async def get_negotiation_status(session_id: str):
    """Get current status of negotiation session"""
    try:
        if session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        session = negotiation_sessions[session_id]
        
        return {
            "success": True,
            "session": session.dict(),
            "progress_percentage": _calculate_progress(session.status)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-negotiations")
async def get_active_negotiations():
    """Get all active negotiation sessions"""
    try:
        active_sessions = [
            session.dict() for session in negotiation_sessions.values()
            if session.status not in ["approved", "rejected"]
        ]
        
        return {
            "success": True,
            "active_sessions": active_sessions,
            "total_count": len(active_sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-approvals")
async def get_pending_approvals():
    """Get negotiations pending user approval"""
    try:
        pending_sessions = [
            session.dict() for session in negotiation_sessions.values()
            if session.status == "pending_approval"
        ]
        
        return {
            "success": True,
            "pending_approvals": pending_sessions,
            "total_count": len(pending_sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-order")
async def approve_order(
    approval: OrderApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject an AI-negotiated order"""
    try:
        if approval.session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        session = negotiation_sessions[approval.session_id]
        
        if session.status != "pending_approval":
            raise HTTPException(status_code=400, detail="Session not ready for approval")
        
        if approval.approved:
            # Create the order
            order = await _create_order_from_proposal(session, db)
            
            # Update stock
            # Get item details for order creation
            result = await db.execute(select(StationeryItem).filter(StationeryItem.id == session.item_id))
            item = result.scalar_one_or_none()
            if item:
                item.current_stock += session.quantity_needed
                await db.commit()
            
            session.status = "approved"
            session.ai_reasoning = f"Order approved by user. Order #{order.order_number} created with {session.best_proposal.vendor_name}"
            
            # Create agent decision record
            decision = AgentDecision(
                decision_type="REORDER",
                item_id=session.item_id,
                vendor_id=session.best_proposal.vendor_id,
                decision_data=json.dumps({
                    "session_id": session.session_id,
                    "quantity": session.quantity_needed,
                    "vendor": session.best_proposal.vendor_name,
                    "total_cost": session.best_proposal.total_price,
                    "order_id": order.id
                }),
                reasoning=f"User approved AI-negotiated order with {session.best_proposal.vendor_name}",
                confidence_score=session.best_proposal.confidence_score,
                is_executed=True,
                executed_at=datetime.now()
            )
            db.add(decision)
            await db.commit()
            
            return {
                "success": True,
                "message": "Order approved and created successfully",
                "order_number": order.order_number,
                "vendor": session.best_proposal.vendor_name,
                "total_cost": session.best_proposal.total_price
            }
        else:
            session.status = "rejected"
            session.ai_reasoning = f"Order rejected by user. Reason: {approval.user_notes or 'No reason provided'}"
            
            return {
                "success": True,
                "message": "Order rejected by user"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel-negotiation/{session_id}")
async def cancel_negotiation(session_id: str):
    """Cancel an ongoing negotiation"""
    try:
        if session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        del negotiation_sessions[session_id]
        
        return {
            "success": True,
            "message": "Negotiation session cancelled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background process functions
async def _run_negotiation_process(session_id: str, db: AsyncSession):
    """Run the complete negotiation process in background"""
    try:
        session = negotiation_sessions[session_id]
        
        # Step 1: Vendor discovery (1-2 seconds)
        await asyncio.sleep(2)
        await _discover_vendors(session, db)
        
        # Step 2: Negotiate with vendors (3-5 seconds)
        await asyncio.sleep(3)
        await _negotiate_with_vendors(session, db)
        
        # Step 3: Compare proposals (1-2 seconds)
        await asyncio.sleep(2)
        await _compare_proposals(session)
        
    except Exception as e:
        if session_id in negotiation_sessions:
            session = negotiation_sessions[session_id]
            session.status = "error"
            session.ai_reasoning = f"Error during negotiation: {str(e)}"

async def _discover_vendors(session: NegotiationSession, db: AsyncSession):
    """Simulate vendor discovery process with conversation tracking"""
    result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE))
    vendors = result.scalars().all()
    
    # Add conversation messages
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message=f"🔍 Scanning vendor database... Found {len(vendors)} active vendors for {session.item_name}",
        message_type="discovery"
    ))
    
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent", 
        message="📋 Analyzing vendor capabilities and performance history...",
        message_type="discovery"
    ))
    
    session.status = "negotiating"
    session.ai_reasoning = f"🔍 Found {len(vendors)} potential vendors. Starting negotiations..."
    session.updated_at = datetime.now()

async def _negotiate_with_vendors(session: NegotiationSession, db: AsyncSession):
    """Negotiate with ALL vendors using real Gemini AI"""
    # Get ALL active vendors instead of limiting to 3
    result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE))
    vendors = result.scalars().all()
    
    if not vendors:
        session.status = "error"
        session.ai_reasoning = "❌ No active vendors found for negotiation"
        session.updated_at = datetime.now()
        return
    
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message=f"📞 Initiating negotiations with ALL {len(vendors)} active vendors...",
        message_type="negotiation"
    ))
    
    proposals = []
    
    for i, vendor in enumerate(vendors):
        # Simulate realistic delay for each vendor negotiation
        await asyncio.sleep(random.uniform(1, 3))
        
        # Use Gemini AI to generate realistic vendor negotiation
        try:
            vendor_context = await _generate_vendor_negotiation_with_gemini(
                session, vendor, i + 1, len(vendors)
            )
            proposal = vendor_context["proposal"]
            conversation_messages = vendor_context["conversation"]
            
            # Add conversation messages
            for msg in conversation_messages:
                session.conversation.append(msg)
            
            proposals.append(proposal)
            
        except Exception as e:
            logger.error(f"Failed to negotiate with vendor {vendor.name}: {str(e)}")
            # Fallback to basic proposal if Gemini fails
            fallback_proposal = _create_fallback_proposal(vendor, session)
            proposals.append(fallback_proposal)
            
            session.conversation.append(ConversationMessage(
                timestamp=datetime.now(),
                speaker="AI Agent",
                message=f"⚠️ Technical issue with {vendor.name} negotiation, using backup pricing",
                message_type="negotiation"
            ))
    
    session.vendor_proposals = proposals
    session.status = "comparing"
    session.ai_reasoning = f"💬 Completed negotiations with {len(proposals)} vendors. Analyzing offers..."
    session.updated_at = datetime.now()

async def _compare_proposals(session: NegotiationSession):
    """Analyze and select best proposal with detailed reasoning"""
    if not session.vendor_proposals:
        session.status = "error"
        session.ai_reasoning = "❌ No proposals received from vendors"
        return
    
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message="🤖 Starting comprehensive proposal analysis...",
        message_type="comparison"
    ))
    
    # Enhanced scoring algorithm with detailed breakdown
    def score_proposal(proposal):
        # Weighted scoring: price (40%), delivery (25%), confidence (20%), special offers (15%)
        price_score = (1.0 / proposal.unit_price) * 100  # Normalized price score
        delivery_score = (1.0 / proposal.delivery_time) * 100  # Faster delivery
        confidence_score = proposal.confidence_score * 100
        special_score = 100 if proposal.special_offers else 70
        
        total_score = (price_score * 0.4) + (delivery_score * 0.25) + (confidence_score * 0.2) + (special_score * 0.15)
        return total_score
    
    # Score all proposals
    scored_proposals = [(proposal, score_proposal(proposal)) for proposal in session.vendor_proposals]
    scored_proposals.sort(key=lambda x: x[1], reverse=True)
    
    # Add detailed analysis to conversation
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message="📊 Proposal Analysis Complete:",
        message_type="comparison"
    ))
    
    for i, (proposal, score) in enumerate(scored_proposals, 1):
        analysis = f"#{i} {proposal.vendor_name}: ${proposal.unit_price:.2f}/unit, {proposal.delivery_time}d delivery, Score: {score:.1f}/100"
        if proposal.special_offers:
            analysis += f" + {proposal.special_offers}"
        
        session.conversation.append(ConversationMessage(
            timestamp=datetime.now(),
            speaker="AI Agent", 
            message=analysis,
            message_type="comparison"
        ))
    
    best_proposal = scored_proposals[0][0]
    best_score = scored_proposals[0][1]
    
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message=f"🏆 RECOMMENDATION: {best_proposal.vendor_name} offers the best value with score {best_score:.1f}/100",
        message_type="comparison"
    ))
    
    session.best_proposal = best_proposal
    session.status = "pending_approval"
    session.ai_reasoning = f"✅ Analysis complete. Recommending {best_proposal.vendor_name}: ${best_proposal.total_price:.2f} total, {best_proposal.delivery_time} day delivery. Awaiting your approval."
    session.updated_at = datetime.now()

async def _create_order_from_proposal(session: NegotiationSession, db: AsyncSession) -> Order:
    """Create order from approved proposal with order items"""
    proposal = session.best_proposal
    
    # Import OrderItem here to avoid circular imports
    from app.models import OrderItem, OrderStatus
    
    order = Order(
        order_number=f"AI-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        vendor_id=proposal.vendor_id,
        status=OrderStatus.PENDING,
        total_amount=proposal.total_price,
        order_date=datetime.now(),
        expected_delivery_date=datetime.now() + timedelta(days=proposal.delivery_time),
        notes=f"AI-negotiated order via session {session.session_id}. Terms: {proposal.terms}. {proposal.special_offers or ''}",
        created_by="AI Agent"
    )
    
    db.add(order)
    await db.flush()  # Get the order ID
    
    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        item_id=session.item_id,
        quantity=session.quantity_needed,
        unit_price=proposal.unit_price,
        total_price=proposal.total_price
    )
    
    db.add(order_item)
    await db.commit()
    await db.refresh(order)
    
    # Add final conversation message
    session.conversation.append(ConversationMessage(
        timestamp=datetime.now(),
        speaker="AI Agent",
        message=f"🎉 Order #{order.order_number} created successfully! Stock will be replenished in {proposal.delivery_time} days.",
        message_type="completion"
    ))
    
    return order

def _calculate_progress(status: str) -> int:
    """Calculate progress percentage based on status"""
    progress_map = {
        "discovering": 25,
        "negotiating": 60,
        "comparing": 85,
        "pending_approval": 100,
        "approved": 100,
        "rejected": 100,
        "error": 100
    }
    return progress_map.get(status, 0)