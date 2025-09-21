"""
AI Agent Negotiation API endpoints for vendor discovery, negotiation, and order approval workflow.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
import uuid
import random
import asyncio

from app.core.database import get_db
from app.models import StationeryItem, Vendor, Order, AgentDecision
from pydantic import BaseModel

router = APIRouter()

# Global storage for negotiation sessions (in production, use database)
negotiation_sessions = {}

# Background negotiation function for auto-refill integration  
async def start_negotiation_background(db: Session, negotiation_data: dict) -> str:
    """Start AI negotiation process in background for auto-refill"""
    try:
        session_id = str(uuid.uuid4())
        
        # Get item details
        item = db.query(StationeryItem).filter(StationeryItem.id == negotiation_data["item_id"]).first()
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

async def simulate_negotiation_process(session_id: str, db: Session):
    """Simulate the complete negotiation process"""
    try:
        session = negotiation_sessions.get(session_id)
        if not session:
            return
        
        # Phase 1: Vendor Discovery (2-5 seconds)
        await asyncio.sleep(random.uniform(2, 5))
        session["status"] = "negotiating"
        session["ai_reasoning"] = f"Found 3 potential vendors for {session['item_name']}. Beginning negotiations..."
        session["updated_at"] = datetime.now().isoformat()
        
        # Phase 2: Negotiation (5-10 seconds)
        await asyncio.sleep(random.uniform(5, 10))
        session["status"] = "comparing"
        session["ai_reasoning"] = f"Completed negotiations with all vendors. Analyzing proposals..."
        
        # Generate vendor proposals
        vendors = db.query(Vendor).limit(3).all()
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

class VendorProposal(BaseModel):
    vendor_id: int
    vendor_name: str
    unit_price: float
    total_price: float
    delivery_time: int  # days
    terms: str
    confidence_score: float

class NegotiationSession(BaseModel):
    session_id: str
    item_id: int
    item_name: str
    quantity_needed: int
    status: str  # discovering, negotiating, comparing, pending_approval, approved, rejected
    vendor_proposals: List[VendorProposal] = []
    best_proposal: Optional[VendorProposal] = None
    ai_reasoning: str
    created_at: datetime
    updated_at: datetime
    
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
    db: Session = Depends(get_db)
):
    """Start AI agent negotiation process for an item"""
    try:
        # Get item details
        item = db.query(StationeryItem).filter(StationeryItem.id == request.item_id).first()
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
    db: Session = Depends(get_db)
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
            item = db.query(StationeryItem).filter(StationeryItem.id == session.item_id).first()
            if item:
                item.current_stock += session.quantity_needed
                db.commit()
            
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
            db.commit()
            
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
async def _run_negotiation_process(session_id: str, db: Session):
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

async def _discover_vendors(session: NegotiationSession, db: Session):
    """Simulate vendor discovery process"""
    vendors = db.query(Vendor).filter(Vendor.is_active == True).all()
    
    session.status = "negotiating"
    session.ai_reasoning = f"🔍 Found {len(vendors)} potential vendors. Starting negotiations..."
    session.updated_at = datetime.now()

async def _negotiate_with_vendors(session: NegotiationSession, db: Session):
    """Simulate negotiations with vendors"""
    vendors = db.query(Vendor).filter(Vendor.is_active == True).limit(3).all()
    proposals = []
    
    for vendor in vendors:
        # Generate realistic proposal with some randomness
        base_price = random.uniform(8, 25)  # Random unit price
        delivery_days = random.randint(3, 14)
        confidence = random.uniform(0.7, 0.95)
        
        proposal = VendorProposal(
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            unit_price=base_price,
            total_price=base_price * session.quantity_needed,
            delivery_time=delivery_days,
            terms=f"Net {random.choice([15, 30, 45])} payment terms, FOB destination",
            confidence_score=confidence
        )
        proposals.append(proposal)
    
    session.vendor_proposals = proposals
    session.status = "comparing"
    session.ai_reasoning = f"💬 Received {len(proposals)} proposals from vendors. Analyzing offers..."
    session.updated_at = datetime.now()

async def _compare_proposals(session: NegotiationSession):
    """Analyze and select best proposal"""
    if not session.vendor_proposals:
        session.status = "error"
        session.ai_reasoning = "❌ No proposals received from vendors"
        return
    
    # Scoring algorithm: consider price, delivery time, and confidence
    def score_proposal(proposal):
        price_score = 1.0 / proposal.unit_price  # Lower price = higher score
        delivery_score = 1.0 / proposal.delivery_time  # Faster delivery = higher score
        return (price_score * 0.5) + (delivery_score * 0.3) + (proposal.confidence_score * 0.2)
    
    best_proposal = max(session.vendor_proposals, key=score_proposal)
    
    session.best_proposal = best_proposal
    session.status = "pending_approval"
    session.ai_reasoning = f"✅ Analysis complete. Recommending {best_proposal.vendor_name}: ${best_proposal.total_price:.2f} total, {best_proposal.delivery_time} day delivery. Awaiting your approval."
    session.updated_at = datetime.now()

async def _create_order_from_proposal(session: NegotiationSession, db: Session) -> Order:
    """Create order from approved proposal"""
    proposal = session.best_proposal
    
    order = Order(
        order_number=f"AI-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        vendor_id=proposal.vendor_id,
        status="PENDING",
        total_amount=proposal.total_price,
        order_date=datetime.now(),
        expected_delivery_date=datetime.now() + timedelta(days=proposal.delivery_time),
        notes=f"AI-negotiated order via session {session.session_id}. Terms: {proposal.terms}",
        created_by="AI Agent"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
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