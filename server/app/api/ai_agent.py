"""
AI Agent Negotiation API endpoints for vendor discovery, negotiation, and order approval workflow.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
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
from app.services.trend_analysis import get_trend_suggestions

router = APIRouter()

# Global storage for negotiation sessions (in production, use database)
negotiation_sessions = {}

# Initialize Gemini agent
gemini_agent = SupplyChainAgent()

# Background negotiation function for auto-refill integration  
async def start_negotiation_background(db: AsyncSession, negotiation_data: dict) -> str:
    """Start AI negotiation process in background for auto-refill"""
    try:
        # Get item details for order creation
        result = await db.execute(select(StationeryItem).filter(StationeryItem.id == negotiation_data["item_id"]))
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError(f"Item {negotiation_data['item_id']} not found")
        
        # Create session ID
        session_id = f"neg_{uuid.uuid4().hex[:8]}"
        
        # Create negotiation session
        session = {
            "session_id": session_id,
            "item_id": negotiation_data["item_id"],
            "item_name": item.name,
            "quantity_needed": negotiation_data["quantity_needed"],
            "status": "discovering",
            "vendor_proposals": [],
            "conversation": [],
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
            session["ai_reasoning"] = f"Found potential vendors for {session['item_name']}. Beginning negotiations..."
        
        session["updated_at"] = datetime.now().isoformat()
        
        # Phase 2: Negotiation (5-10 seconds)
        await asyncio.sleep(random.uniform(5, 10))
        session["status"] = "comparing"
        session["ai_reasoning"] = f"Completed negotiations with all vendors. Analyzing proposals..."
        
        # Generate vendor proposals using async query
        await _discover_vendors_simple(session, db)
        await _negotiate_with_vendors_gemini(session, db)
        await _compare_proposals_enhanced(session)
        
        session["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        if session_id in negotiation_sessions:
            session = negotiation_sessions[session_id]
            session["status"] = "error"
            session["ai_reasoning"] = f"Error during negotiation: {str(e)}"

# Pydantic Models for conversation tracking
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

class NegotiationRequest(BaseModel):
    item_id: int
    quantity_needed: int
    max_budget: Optional[float] = None
    urgency: str = "medium"  # low, medium, high

class OrderApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    user_notes: Optional[str] = None

class QuickActionRequest(BaseModel):
    session_id: str
    action: str  # price_match, expedite, bulk_discount, accept_terms
    message: str

class TrendSuggestion(BaseModel):
    trend: str
    product: str
    sku: str
    reason: str

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
        
        # Create negotiation session
        session_id = f"neg_{uuid.uuid4().hex[:8]}"
        session = NegotiationSession(
            session_id=session_id,
            item_id=request.item_id,
            item_name=item.name,
            quantity_needed=request.quantity_needed,
            status="discovering",
            vendor_proposals=[],
            conversation=[],
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
            "session": session.dict() if hasattr(session, 'dict') else session,
            "progress_percentage": _calculate_progress(session.status if hasattr(session, 'status') else session.get('status'))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-negotiations")
async def get_active_negotiations():
    """Get all active negotiation sessions"""
    try:
        active_sessions = []
        for session in negotiation_sessions.values():
            status = session.status if hasattr(session, 'status') else session.get('status')
            if status not in ["approved", "rejected"]:
                session_dict = session.dict() if hasattr(session, 'dict') else session
                active_sessions.append(session_dict)
        
        return {
            "success": True,
            "active_sessions": active_sessions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-approvals")
async def get_pending_approvals():
    """Get negotiations waiting for approval"""
    try:
        pending_sessions = []
        for session in negotiation_sessions.values():
            status = session.status if hasattr(session, 'status') else session.get('status')
            if status == "pending_approval":
                session_dict = session.dict() if hasattr(session, 'dict') else session
                pending_sessions.append(session_dict)
        
        return {
            "success": True,
            "pending_approvals": pending_sessions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_notifications():
    """Get real-time notifications from AI agent activities"""
    try:
        notifications = []
        
        # Generate notifications from active negotiation sessions
        for session in negotiation_sessions.values():
            status = session.status if hasattr(session, 'status') else session.get('status')
            session_id = session.session_id if hasattr(session, 'session_id') else session.get('session_id')
            item_name = session.item_name if hasattr(session, 'item_name') else session.get('item_name')
            quantity = session.quantity_needed if hasattr(session, 'quantity_needed') else session.get('quantity_needed')
            best_proposal = session.best_proposal if hasattr(session, 'best_proposal') else session.get('best_proposal')
            
            if status == "pending_approval" and best_proposal:
                vendor_name = best_proposal.vendor_name if hasattr(best_proposal, 'vendor_name') else best_proposal.get('vendor_name', 'Unknown Vendor')
                total_cost = best_proposal.total_price if hasattr(best_proposal, 'total_price') else best_proposal.get('total_price', 0)
                delivery_time = best_proposal.delivery_time if hasattr(best_proposal, 'delivery_time') else best_proposal.get('delivery_time', 0)
                
                notifications.append({
                    "id": f"approval_{session_id}",
                    "type": "approval_request",
                    "title": "Order Approval Required",
                    "message": f"AI agent found the best deal for {item_name} (Qty: {quantity}) from {vendor_name} for ${total_cost:.2f}. Approval needed to proceed.",
                    "metadata": {
                        "session_id": session_id,
                        "item_name": item_name,
                        "vendor_name": vendor_name,
                        "total_cost": total_cost,
                        "delivery_time": delivery_time,
                        "quantity": quantity
                    },
                    "created_at": session.updated_at if hasattr(session, 'updated_at') else session.get('updated_at', datetime.now().isoformat()),
                    "read": False,
                    "requires_action": True
                })
            elif status == "negotiating":
                notifications.append({
                    "id": f"negotiating_{session_id}",
                    "type": "info",
                    "title": "AI Negotiation in Progress",
                    "message": f"AI agent is actively negotiating with vendors for {item_name} (Qty: {quantity}). Progress updates coming soon.",
                    "metadata": {
                        "session_id": session_id,
                        "item_name": item_name,
                        "quantity": quantity
                    },
                    "created_at": session.updated_at if hasattr(session, 'updated_at') else session.get('updated_at', datetime.now().isoformat()),
                    "read": False,
                    "requires_action": False
                })
        
        return {
            "success": True,
            "notifications": notifications
        }
        
    except Exception as e:
        logger.error(f"Failed to get notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-low-stock-negotiations")
async def trigger_low_stock_negotiations(db: AsyncSession = Depends(get_db)):
    """Trigger AI negotiations for all items currently below reorder level"""
    try:
        # Get all items below reorder level
        result = await db.execute(
            select(StationeryItem).where(
                StationeryItem.current_stock <= StationeryItem.reorder_level,
                StationeryItem.is_active == True
            )
        )
        low_stock_items = result.scalars().all()
        
        triggered_sessions = []
        
        for item in low_stock_items:
            # Check if there's already an active negotiation for this item
            existing_session = None
            for session in negotiation_sessions.values():
                item_id = session.item_id if hasattr(session, 'item_id') else session.get('item_id')
                status = session.status if hasattr(session, 'status') else session.get('status')
                if item_id == item.id and status in ['discovering', 'negotiating', 'pending_approval']:
                    existing_session = session
                    break
            
            if not existing_session:
                # Calculate recommended quantity to reach max stock level
                recommended_quantity = max(item.max_stock_level - item.current_stock, item.reorder_level)
                
                # Start AI negotiation process
                negotiation_data = {
                    "item_id": item.id,
                    "quantity_needed": recommended_quantity,
                    "urgency": "high" if item.current_stock == 0 else "medium",
                    "trigger_source": "low_stock_check",
                    "context": {
                        "current_stock": item.current_stock,
                        "reorder_level": item.reorder_level,
                        "max_stock_level": item.max_stock_level
                    }
                }
                
                session_id = await start_negotiation_background(db, negotiation_data)
                triggered_sessions.append({
                    "session_id": session_id,
                    "item_name": item.name,
                    "current_stock": item.current_stock,
                    "quantity_needed": recommended_quantity
                })
        
        return {
            "success": True,
            "message": f"Triggered {len(triggered_sessions)} AI negotiations for low stock items",
            "triggered_sessions": triggered_sessions,
            "total_low_stock_items": len(low_stock_items)
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger low stock negotiations: {str(e)}")
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
        session_status = session.status if hasattr(session, 'status') else session.get('status')
        
        if session_status != "pending_approval":
            raise HTTPException(status_code=400, detail="Session not ready for approval")
        
        if approval.approved:
            # Create the order
            order = await _create_order_from_proposal(session, db)
            
            # Update stock
            item_id = session.item_id if hasattr(session, 'item_id') else session.get('item_id')
            quantity = session.quantity_needed if hasattr(session, 'quantity_needed') else session.get('quantity_needed')
            
            result = await db.execute(select(StationeryItem).filter(StationeryItem.id == item_id))
            item = result.scalar_one_or_none()
            if item:
                item.current_stock += quantity
                await db.commit()
            
            # Update session status
            if hasattr(session, 'status'):
                session.status = "approved"
                session.ai_reasoning = f"Order approved by user. Order #{order.order_number} created"
            else:
                session['status'] = "approved"
                session['ai_reasoning'] = f"Order approved by user. Order #{order.order_number} created"
            
            return {
                "success": True,
                "message": "Order approved and created successfully",
                "order_number": order.order_number,
                "total_cost": order.total_amount
            }
        else:
            # Update session status for rejection
            if hasattr(session, 'status'):
                session.status = "rejected"
                session.ai_reasoning = f"Order rejected by user. Reason: {approval.user_notes or 'No reason provided'}"
            else:
                session['status'] = "rejected"
                session['ai_reasoning'] = f"Order rejected by user. Reason: {approval.user_notes or 'No reason provided'}"
            
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
            "message": "Negotiation cancelled successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-action")
async def send_quick_action(
    action_request: QuickActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a quick action to an ongoing negotiation"""
    try:
        if action_request.session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        session = negotiation_sessions[action_request.session_id]
        
        # Add the quick action to conversation
        conversation_message = {
            "timestamp": datetime.now().isoformat(),
            "speaker": "User",
            "message": action_request.message,
            "message_type": f"quick_action_{action_request.action}"
        }
        
        if hasattr(session, 'conversation'):
            session.conversation.append(conversation_message)
        else:
            session['conversation'].append(conversation_message)
        
        # Process the quick action based on type
        ai_response = await _process_quick_action(session, action_request.action, action_request.message, db)
        
        # Add AI response to conversation
        ai_message = {
            "timestamp": datetime.now().isoformat(),
            "speaker": "AI Agent",
            "message": ai_response,
            "message_type": "quick_response"
        }
        
        if hasattr(session, 'conversation'):
            session.conversation.append(ai_message)
        else:
            session['conversation'].append(ai_message)
        
        return {
            "success": True,
            "message": f"Quick action '{action_request.action}' processed successfully",
            "ai_response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Quick action failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background process functions
async def _process_quick_action(session, action: str, message: str, db: AsyncSession) -> str:
    """Process a quick action request with Gemini AI"""
    try:
        # Use Gemini to process the quick action
        prompt = f"""
        As an AI negotiation agent, process this quick action request:
        
        Action Type: {action}
        User Message: {message}
        
        Current negotiation context:
        - Item: {session.get('item_name', 'Unknown')}
        - Quantity: {session.get('quantity_needed', 'Unknown')}
        - Current Status: {session.get('status', 'Unknown')}
        
        Provide a professional response that acknowledges the request and explains what action will be taken.
        Keep the response concise and actionable.
        """
        
        response = await gemini_agent._call_gemini_api(prompt)
        
        # Based on action type, update session appropriately
        if action == "accept_terms" and session.get('status') == 'negotiating':
            # Move to approval stage
            if hasattr(session, 'status'):
                session.status = "pending_approval"
            else:
                session['status'] = "pending_approval"
            
        return response[:200] + "..." if len(response) > 200 else response
        
    except Exception as e:
        logger.error(f"Quick action processing failed: {str(e)}")
        return f"Processing {action} request. Will update negotiation accordingly."

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
            if hasattr(session, 'status'):
                session.status = "error"
                session.ai_reasoning = f"Error during negotiation: {str(e)}"
            else:
                session['status'] = "error"
                session['ai_reasoning'] = f"Error during negotiation: {str(e)}"

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

async def _create_order_from_proposal(session, db: AsyncSession) -> Order:
    """Create order from approved proposal with order items"""
    # Handle both Pydantic models and dict sessions
    best_proposal = session.best_proposal if hasattr(session, 'best_proposal') else session.get('best_proposal')
    session_id = session.session_id if hasattr(session, 'session_id') else session.get('session_id')
    item_id = session.item_id if hasattr(session, 'item_id') else session.get('item_id')
    quantity = session.quantity_needed if hasattr(session, 'quantity_needed') else session.get('quantity_needed')
    
    # Import OrderItem and OrderStatus here to avoid circular imports
    from app.models import OrderItem, OrderStatus
    
    order = Order(
        order_number=f"AI-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        vendor_id=best_proposal.vendor_id if hasattr(best_proposal, 'vendor_id') else best_proposal['vendor_id'],
        status=OrderStatus.PENDING,
        total_amount=best_proposal.total_price if hasattr(best_proposal, 'total_price') else best_proposal['total_price'],
        order_date=datetime.now(),
        expected_delivery_date=datetime.now() + timedelta(days=best_proposal.delivery_time if hasattr(best_proposal, 'delivery_time') else best_proposal['delivery_time']),
        notes=f"AI-negotiated order via session {session_id}.",
        created_by="AI Agent"
    )
    
    db.add(order)
    await db.flush()  # Get the order ID
    
    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        item_id=item_id,
        quantity_ordered=quantity,
        unit_price=best_proposal.unit_price if hasattr(best_proposal, 'unit_price') else best_proposal['unit_price'],
        total_price=best_proposal.total_price if hasattr(best_proposal, 'total_price') else best_proposal['total_price']
    )
    
    db.add(order_item)
    await db.commit()
    await db.refresh(order)
    
    return order

async def _generate_vendor_negotiation_with_gemini(
    session: NegotiationSession, 
    vendor: Vendor, 
    vendor_index: int, 
    total_vendors: int
) -> Dict[str, Any]:
    """Generate realistic vendor negotiation using Gemini AI"""
    
    # Create negotiation context for Gemini
    negotiation_prompt = f"""
You are a vendor representative in a supply chain negotiation. Respond as {vendor.name} would.

CONTEXT:
- Item: {session.item_name}
- Quantity: {session.quantity_needed}
- Your company: {vendor.name}
- Your reliability score: {vendor.reliability_score}/10
- Your average delivery: {vendor.avg_delivery_days} days

Provide a competitive business proposal. Consider your company's reputation and capabilities.

IMPORTANT: Respond with ONLY a valid JSON object in this exact format:
{{
    "vendor_greeting": "Professional greeting acknowledging the request",
    "vendor_quote": "Your pricing proposal with details",
    "unit_price": 15.50,
    "delivery_days": 7,
    "special_offers": "Any special terms or null",
    "confidence_score": 0.85,
    "payment_terms": "Payment terms offered",
    "additional_notes": "Any additional comments"
}}

Pricing should be realistic ($8-30/unit). Delivery should reflect your average ({vendor.avg_delivery_days} days ±3).
Higher reliability scores should offer better terms and pricing.
"""
    
    try:
        # Use Gemini agent for realistic negotiation
        response = await gemini_agent._call_gemini_api(negotiation_prompt)
        
        # Clean and parse Gemini response
        try:
            # Remove any markdown code blocks or extra text
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON-like content
            start_brace = cleaned_response.find('{')
            end_brace = cleaned_response.rfind('}')
            if start_brace != -1 and end_brace != -1:
                json_content = cleaned_response[start_brace:end_brace+1]
                negotiation_data = json.loads(json_content)
            else:
                # If no JSON found, create structured response from text
                negotiation_data = _parse_text_response(cleaned_response, vendor, session)
                
        except (json.JSONDecodeError, ValueError) as parse_error:
            logger.warning(f"Failed to parse Gemini JSON for {vendor.name}: {str(parse_error)}")
            # Create structured response from text
            negotiation_data = _parse_text_response(response, vendor, session)
        
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

def _parse_text_response(response_text: str, vendor: Vendor, session: NegotiationSession) -> Dict[str, Any]:
    """Parse non-JSON Gemini response into structured data"""
    import re
    
    # Extract pricing information using regex
    price_patterns = [
        r'\$?(\d+\.?\d*)\s*per\s*unit',
        r'\$?(\d+\.?\d*)\s*/\s*unit',
        r'price.*?\$?(\d+\.?\d*)',
        r'quote.*?\$?(\d+\.?\d*)',
        r'\$(\d+\.?\d*)'
    ]
    
    unit_price = None
    for pattern in price_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            try:
                unit_price = float(match.group(1))
                if 5 <= unit_price <= 50:  # Reasonable range
                    break
            except ValueError:
                continue
    
    if unit_price is None:
        unit_price = random.uniform(8, 25)  # Fallback
    
    # Extract delivery information
    delivery_patterns = [
        r'(\d+)\s*days?\s*delivery',
        r'delivery.*?(\d+)\s*days?',
        r'(\d+)\s*day\s*delivery'
    ]
    
    delivery_days = None
    for pattern in delivery_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            try:
                delivery_days = int(match.group(1))
                if 1 <= delivery_days <= 30:  # Reasonable range
                    break
            except ValueError:
                continue
    
    if delivery_days is None:
        delivery_days = random.randint(5, 15)  # Fallback
    
    # Look for special offers
    special_offers = None
    offer_keywords = ['discount', 'free shipping', 'warranty', 'bulk', 'early payment']
    for keyword in offer_keywords:
        if keyword in response_text.lower():
            # Extract the sentence containing the offer
            sentences = response_text.split('.')
            for sentence in sentences:
                if keyword in sentence.lower():
                    special_offers = sentence.strip()
                    break
            break
    
    # Create greeting and quote messages
    if 'hello' in response_text.lower() or 'hi' in response_text.lower():
        greeting_end = min(len(response_text), 100)
        vendor_greeting = response_text[:greeting_end].strip()
    else:
        vendor_greeting = f"Hello! We can supply {session.item_name}. Let me check our pricing..."
    
    vendor_quote = f"Our quote is ${unit_price:.2f}/unit with {delivery_days} day delivery."
    if special_offers:
        vendor_quote += f" {special_offers}"
    
    return {
        "vendor_greeting": vendor_greeting,
        "vendor_quote": vendor_quote,
        "unit_price": unit_price,
        "delivery_days": delivery_days,
        "special_offers": special_offers,
        "confidence_score": vendor.reliability_score / 10.0,
        "payment_terms": "Net 30 payment terms",
        "additional_notes": "Parsed from AI response"
    }


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
    }

# Simplified helper functions for background processing
async def _discover_vendors_simple(session: dict, db: AsyncSession):
    """Simple vendor discovery for background processing"""
    result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE))
    vendors = result.scalars().all()
    
    session["ai_reasoning"] = f"🔍 Found {len(vendors)} potential vendors. Starting negotiations..."
    session["updated_at"] = datetime.now().isoformat()

async def _negotiate_with_vendors_gemini(session: dict, db: AsyncSession):
    """Enhanced vendor negotiation with Gemini for background processing"""
    result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE))
    vendors = result.scalars().all()
    
    proposals = []
    
    for vendor in vendors:
        try:
            # Use Gemini AI for realistic negotiation
            negotiation_prompt = f"""
You are {vendor.name} negotiating a supply contract.

DETAILS:
- Item: {session['item_name']}
- Quantity: {session['quantity_needed']}
- Your reliability: {vendor.reliability_score}/10
- Your delivery time: {vendor.avg_delivery_days} days average

Provide a competitive quote. Higher reliability should mean better pricing.

Respond with ONLY valid JSON:
{{
    "unit_price": 15.50,
    "delivery_days": 7,
    "confidence": 0.85,
    "special_offer": "Optional offer or null"
}}
"""
            
            response = await gemini_agent._call_gemini_api(negotiation_prompt)
            
            # Enhanced parsing with fallback
            try:
                # Clean response
                cleaned = response.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].split("```")[0].strip()
                
                # Extract JSON
                start_brace = cleaned.find('{')
                end_brace = cleaned.rfind('}')
                if start_brace != -1 and end_brace != -1:
                    json_content = cleaned[start_brace:end_brace+1]
                    data = json.loads(json_content)
                    
                    unit_price = float(data.get("unit_price", random.uniform(8, 25)))
                    delivery_days = int(data.get("delivery_days", random.randint(5, 15)))
                    confidence = float(data.get("confidence", random.uniform(0.7, 0.95)))
                else:
                    raise ValueError("No JSON found")
                    
            except (json.JSONDecodeError, ValueError, KeyError):
                # Fallback values
                unit_price = random.uniform(8, 25)
                delivery_days = random.randint(5, 15)
                confidence = random.uniform(0.7, 0.95)
            
        except Exception as e:
            # Complete fallback
            unit_price = random.uniform(8, 25)
            delivery_days = random.randint(5, 15)
            confidence = random.uniform(0.7, 0.95)
        
        proposal = {
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "unit_price": unit_price,
            "total_price": unit_price * session['quantity_needed'],
            "delivery_time": delivery_days,
            "confidence_score": confidence,
            "terms": "Net 30 payment terms"
        }
        proposals.append(proposal)
    
    session["vendor_proposals"] = proposals
    session["ai_reasoning"] = f"💬 Completed negotiations with {len(proposals)} vendors. Analyzing offers..."
    session["updated_at"] = datetime.now().isoformat()

async def _compare_proposals_enhanced(session: dict):
    """Enhanced proposal comparison for background processing"""
    proposals = session.get("vendor_proposals", [])
    
    if not proposals:
        session["status"] = "error"
        session["ai_reasoning"] = "❌ No proposals received from vendors"
        return
    
    # Score proposals
    def score_proposal(proposal):
        price_score = (1.0 / proposal["unit_price"]) * 100
        delivery_score = (1.0 / proposal["delivery_time"]) * 100
        confidence_score = proposal["confidence_score"] * 100
        return (price_score * 0.5) + (delivery_score * 0.3) + (confidence_score * 0.2)
    
    best_proposal = max(proposals, key=score_proposal)
    
    session["best_proposal"] = best_proposal
    session["status"] = "pending_approval"
    session["ai_reasoning"] = f"✅ Analysis complete. Recommending {best_proposal['vendor_name']}: ${best_proposal['total_price']:.2f} total, {best_proposal['delivery_time']} day delivery. Awaiting your approval."
    session["updated_at"] = datetime.now().isoformat()

def _calculate_progress(status: str) -> int:
    """Calculate progress percentage based on negotiation status"""
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

@router.get("/ai-suggestions", response_model=List[TrendSuggestion])
async def get_ai_suggestions():
    """Get AI product suggestions based on current trends (festivals, school start, exams, etc.)"""
    return get_trend_suggestions()