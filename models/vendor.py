"""
Data models for vendors and offers
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime

@dataclass
class Vendor:
    id: str
    name: str
    reliability_score: float
    past_performance: float
    contact_info: Dict[str, str]
    payment_terms: List[str]
    specialties: List[str]
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "reliability_score": self.reliability_score,
            "past_performance": self.past_performance,
            "contact_info": self.contact_info,
            "payment_terms": self.payment_terms,
            "specialties": self.specialties
        }

@dataclass
class VendorOffer:
    vendor_id: str
    price: Decimal
    delivery_days: int
    terms: Dict[str, Any]
    validity_period: int  # in days
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "vendor_id": self.vendor_id,
            "price": float(self.price),
            "delivery_days": self.delivery_days,
            "terms": self.terms,
            "validity_period": self.validity_period,
            "created_at": self.created_at.isoformat()
        }
    
    def is_valid(self):
        expiration = self.created_at + timedelta(days=self.validity_period)
        return datetime.now() < expiration