"""
AI Agent Negotiation API endpoints for vendor discovery, negotiation, and order approval workflow.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
import uuid

from app.models.database import get_db, StationeryItem, Vendor, Order, AgentDecision
from app.services.database import DatabaseService
from app.services.gemini_client import GeminiClient
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai-agent", tags=["AI Agent"])

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
    vendor_proposals: List[VendorProposal]
    best_proposal: Optional[VendorProposal]
    ai_reasoning: str
    created_at: datetime
    updated_at: datetime

class OrderApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    user_notes: Optional[str] = None

# Global storage for negotiation sessions (in production, use database)
negotiation_sessions = {}

@router.post("/start-negotiation", response_model=dict)
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
async def get_negotiation_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get current status of negotiation session"""
    try:
        if session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        session = negotiation_sessions[session_id]
        
        # Simulate AI agent progress
        await _simulate_negotiation_progress(session, db)
        
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

# Helper functions
async def _simulate_negotiation_progress(session: NegotiationSession, db: Session):
    """Simulate AI agent negotiation progress"""
    import random
    import time
    
    if session.status == "discovering":
        # Simulate vendor discovery
        vendors = db.query(Vendor).filter(Vendor.is_active == True).all()
        
        # Add some delay to simulate real processing
        time.sleep(1)
        
        session.status = "negotiating"
        session.ai_reasoning = f"Found {len(vendors)} potential vendors. Starting negotiations..."
        session.updated_at = datetime.now()
        
    elif session.status == "negotiating":
        # Simulate negotiations with vendors
        vendors = db.query(Vendor).filter(Vendor.is_active == True).limit(3).all()
        proposals = []
        
        for vendor in vendors:
            # Generate realistic proposal
            base_price = random.uniform(10, 50)
            proposal = VendorProposal(
                vendor_id=vendor.id,
                vendor_name=vendor.name,
                unit_price=base_price,
                total_price=base_price * session.quantity_needed,
                delivery_time=random.randint(3, 14),
                terms=f"Net {random.choice([15, 30, 45])} payment terms",
                confidence_score=random.uniform(0.7, 0.95)
            )
            proposals.append(proposal)
        
        session.vendor_proposals = proposals
        session.status = "comparing"
        session.ai_reasoning = f"Received {len(proposals)} proposals. Analyzing and comparing offers..."
        session.updated_at = datetime.now()
        
    elif session.status == "comparing":
        # Select best proposal
        if session.vendor_proposals:
            # Simple algorithm: best price with good delivery time
            best_proposal = min(
                session.vendor_proposals,
                key=lambda p: p.total_price + (p.delivery_time * 10)  # Weight delivery time
            )
            
            session.best_proposal = best_proposal
            session.status = "pending_approval"
            session.ai_reasoning = f"Analysis complete. Recommending {best_proposal.vendor_name} - Best value at ${best_proposal.total_price:.2f} with {best_proposal.delivery_time} day delivery."
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
        expected_delivery_date=datetime.now(),
        notes=f"AI-negotiated order via session {session.session_id}",
        created_by="AI Agent"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order

def _calculate_progress(status: str) -> int:
    """Calculate progress percentage based on status"""
    progress_map = {
        "discovering": 20,
        "negotiating": 50,
        "comparing": 80,
        "pending_approval": 100,
        "approved": 100,
        "rejected": 100
    }
    return progress_map.get(status, 0)