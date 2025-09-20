"""
API endpoints for supplier negotiation chat system.
Provides real-time negotiation interface with AI-powered suppliers.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.negotiation_chat import get_negotiation_chat_manager, initialize_negotiation_chat

router = APIRouter(prefix="/api/negotiations", tags=["negotiations"])

# Pydantic models for API
class StartNegotiationRequest(BaseModel):
    item_sku: str = Field(..., description="SKU of the item to negotiate")
    item_name: str = Field(..., description="Name of the item")
    initial_price: float = Field(..., gt=0, description="Initial quoted price")
    target_price: float = Field(..., gt=0, description="Target price to achieve")
    supplier_id: str = Field(..., description="Supplier identifier")
    quantity: int = Field(default=100, gt=0, description="Quantity to order")

class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message to send to supplier")

class NegotiationSession(BaseModel):
    session_id: str
    item_name: str
    supplier_name: str
    initial_price: float
    current_offer: Optional[float]
    target_price: float
    phase: str
    message_count: int
    last_activity: str
    last_message: Optional[str]
    estimated_savings: float

class ChatMessage(BaseModel):
    id: str
    sender: str
    sender_type: str
    content: str
    timestamp: str
    metadata: Dict[str, Any] = {}

class NegotiationChat(BaseModel):
    session_id: str
    item_name: str
    supplier_name: str
    supplier_contact: str
    phase: str
    is_active: bool
    initial_price: float
    current_offer: Optional[float]
    target_price: float
    created_at: str
    last_activity: str
    messages: List[ChatMessage]
    metadata: Dict[str, Any]

class NegotiationSummary(BaseModel):
    total_negotiations: int
    active_negotiations: int
    successful_negotiations: int
    total_savings: float
    average_savings_per_negotiation: float
    success_rate: float

@router.on_event("startup")
async def startup_event():
    """Initialize negotiation chat system on startup."""
    await initialize_negotiation_chat()

@router.post("/start", response_model=Dict[str, str])
async def start_negotiation(request: StartNegotiationRequest, background_tasks: BackgroundTasks):
    """
    Start a new negotiation session with a supplier.
    
    This endpoint initiates an AI-powered negotiation chat with the specified supplier
    for the given item. The system will automatically send an initial inquiry and
    handle the negotiation flow.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        # Validate supplier exists
        if request.supplier_id not in chat_manager.suppliers:
            available_suppliers = list(chat_manager.suppliers.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Supplier '{request.supplier_id}' not found. Available suppliers: {available_suppliers}"
            )
        
        # Validate pricing logic
        if request.target_price >= request.initial_price:
            raise HTTPException(
                status_code=400,
                detail="Target price must be lower than initial price for negotiation"
            )
        
        # Start negotiation
        session_id = await chat_manager.start_negotiation(
            item_sku=request.item_sku,
            item_name=request.item_name,
            initial_price=request.initial_price,
            target_price=request.target_price,
            supplier_id=request.supplier_id,
            quantity=request.quantity
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "message": f"Negotiation started with {chat_manager.suppliers[request.supplier_id]['company']}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start negotiation: {str(e)}")

@router.post("/{session_id}/send", response_model=Dict[str, Any])
async def send_message(session_id: str, request: SendMessageRequest):
    """
    Send a message in an active negotiation.
    
    Send a negotiation message to the supplier. The AI system will analyze
    the message, extract any price offers, and generate an appropriate
    supplier response based on their personality and negotiation strategy.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        result = await chat_manager.send_message(session_id, request.message)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/active", response_model=List[NegotiationSession])
async def get_active_negotiations():
    """
    Get all active negotiation sessions.
    
    Returns a list of currently active negotiations with summary information
    including current offers, progress, and estimated savings.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        active_sessions = await chat_manager.get_active_negotiations()
        return active_sessions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active negotiations: {str(e)}")

@router.get("/{session_id}/chat", response_model=NegotiationChat)
async def get_negotiation_chat(session_id: str):
    """
    Get complete chat history for a negotiation session.
    
    Returns the full conversation history, current status, pricing information,
    and metadata for the specified negotiation session.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        chat_data = await chat_manager.get_negotiation_chat(session_id)
        
        if "error" in chat_data:
            raise HTTPException(status_code=404, detail=chat_data["error"])
        
        return chat_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get negotiation chat: {str(e)}")

@router.get("/summary", response_model=NegotiationSummary)
async def get_negotiation_summary():
    """
    Get summary statistics for all negotiations.
    
    Returns aggregate statistics including total negotiations, success rate,
    total savings achieved, and other key performance indicators.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        summary = await chat_manager.get_negotiation_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get negotiation summary: {str(e)}")

@router.get("/suppliers", response_model=Dict[str, Any])
async def get_available_suppliers():
    """
    Get list of available suppliers for negotiations.
    
    Returns detailed information about all suppliers including their
    specialties, personalities, and contact information.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        suppliers_info = {}
        
        for supplier_id, supplier_data in chat_manager.suppliers.items():
            suppliers_info[supplier_id] = {
                "id": supplier_id,
                "name": supplier_data["name"],
                "company": supplier_data["company"],
                "email": supplier_data["email"],
                "personality": supplier_data["personality"]["name"],
                "personality_description": supplier_data["personality"]["description"],
                "specialties": supplier_data["specialties"],
                "response_time": f"{supplier_data['response_delay'][0]}-{supplier_data['response_delay'][1]} minutes",
                "availability": supplier_data["availability"],
                "price_flexibility": f"{supplier_data['personality']['price_flexibility'] * 100:.0f}% max discount"
            }
        
        return {
            "suppliers": suppliers_info,
            "total_suppliers": len(suppliers_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suppliers: {str(e)}")

@router.delete("/{session_id}", response_model=Dict[str, str])
async def close_negotiation(session_id: str):
    """
    Close an active negotiation session.
    
    Manually close a negotiation session. This is useful if you want to
    end negotiations without reaching an agreement.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        if session_id not in chat_manager.active_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        session = chat_manager.active_sessions[session_id]
        session.is_active = False
        session.phase = "concluded"
        
        # Add closing message
        session.add_message(
            sender="System",
            sender_type="system",
            content="Negotiation manually closed by user.",
            metadata={"action": "manual_close"}
        )
        
        return {
            "session_id": session_id,
            "status": "closed",
            "message": "Negotiation session closed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close negotiation: {str(e)}")

# Demo/Testing endpoints

@router.post("/demo/start-sample", response_model=Dict[str, Any])
async def start_sample_negotiation():
    """
    Start a sample negotiation for demonstration purposes.
    
    Creates a demo negotiation with realistic data to showcase
    the negotiation system capabilities.
    """
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        if not chat_manager:
            raise HTTPException(status_code=500, detail="Negotiation chat system not initialized")
        
        # Sample negotiation data
        sample_items = [
            {
                "sku": "PEN001",
                "name": "Premium Ball Point Pens (Box of 50)",
                "initial_price": 450.00,
                "target_price": 380.00,
                "supplier": "rajesh_stationery"
            },
            {
                "sku": "NOTE001", 
                "name": "A4 Ruled Notebooks (Pack of 10)",
                "initial_price": 280.00,
                "target_price": 240.00,
                "supplier": "modern_office"
            },
            {
                "sku": "MARK001",
                "name": "Whiteboard Markers Set",
                "initial_price": 320.00,
                "target_price": 280.00,
                "supplier": "creative_arts"
            }
        ]
        
        # Start random sample negotiation
        import random
        sample = random.choice(sample_items)
        
        session_id = await chat_manager.start_negotiation(
            item_sku=sample["sku"],
            item_name=sample["name"],
            initial_price=sample["initial_price"],
            target_price=sample["target_price"],
            supplier_id=sample["supplier"],
            quantity=100
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "sample_data": sample,
            "message": "Sample negotiation started for demonstration"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start sample negotiation: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for the negotiation system."""
    try:
        chat_manager = await get_negotiation_chat_manager()
        
        return {
            "status": "healthy" if chat_manager else "not_initialized",
            "active_sessions": len(chat_manager.active_sessions) if chat_manager else 0,
            "available_suppliers": len(chat_manager.suppliers) if chat_manager else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }