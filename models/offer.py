"""
Offer data models for negotiation system
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OfferStatus(Enum):
    PENDING = "pending"
    COUNTERED = "countered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class NegotiationOffer:
    offer_id: str
    vendor_id: str
    buyer_id: str
    price: Decimal
    delivery_days: int
    terms: Dict[str, Any]
    status: OfferStatus
    previous_offer_id: str = None
    created_at: datetime = None
    expires_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=7)
    
    def to_dict(self):
        return {
            "offer_id": self.offer_id,
            "vendor_id": self.vendor_id,
            "buyer_id": self.buyer_id,
            "price": float(self.price),
            "delivery_days": self.delivery_days,
            "terms": self.terms,
            "status": self.status.value,
            "previous_offer_id": self.previous_offer_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
    
    def is_expired(self):
        return datetime.now() > self.expires_at