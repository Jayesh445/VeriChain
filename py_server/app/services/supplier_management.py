"""
Advanced Supplier Management System with Email Integration and AI Negotiations
Handles supplier discovery, price negotiations, and automated procurement decisions.
"""

import asyncio
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random
import json
from uuid import uuid4

from app.models.database import InventoryItem, SalesDataDB
from app.models import SupplierInfo
from app.services.database import db_manager
from app.services.gemini_client import GeminiClient
from app.services.notifications import notification_manager

class NegotiationStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    AWAITING_RESPONSE = "awaiting_response"
    AGREED = "agreed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    
    @classmethod
    def from_string(cls, status_str: str):
        """Convert string to NegotiationStatus."""
        for status in cls:
            if status.value == status_str:
                return status
        return cls.IN_PROGRESS

class CommunicationChannel(Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    API = "api"

@dataclass
class PriceQuotation:
    """Price quotation from supplier."""
    supplier_id: str
    supplier_name: str
    item_sku: str
    unit_price: float
    minimum_quantity: int
    discount_tiers: Dict[int, float]  # quantity -> discount %
    delivery_time: int
    payment_terms: str
    validity_days: int
    special_conditions: List[str]
    confidence_score: float
    created_at: datetime

@dataclass
class NegotiationRound:
    """Single round in supplier negotiation."""
    round_number: int
    our_offer: float
    supplier_response: float
    our_justification: str
    supplier_justification: str
    status: NegotiationStatus
    timestamp: datetime

@dataclass
class SupplierPerformance:
    """Supplier performance metrics."""
    supplier_id: str
    total_orders: int
    avg_delivery_time: float
    quality_rating: float
    on_time_delivery_rate: float
    price_competitiveness: float
    communication_rating: float
    overall_score: float
    last_updated: datetime

class SupplierManager:
    """Advanced supplier management with AI-powered negotiations."""
    
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        
        # Email configuration
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "verichain.procurement@gmail.com",
            "password": "your_app_password",  # Use app password
            "sender_name": "VeriChain Procurement Team"
        }
        
        # Active negotiations tracking
        self.active_negotiations: Dict[str, List[NegotiationRound]] = {}
        self.price_quotations: Dict[str, List[PriceQuotation]] = {}
        
        # Supplier performance cache
        self.supplier_performance: Dict[str, SupplierPerformance] = {}
    
    async def request_quotations(self, item: InventoryItem, quantity: int, 
                               urgency: str = "normal") -> List[PriceQuotation]:
        """Request price quotations from multiple suppliers."""
        print(f"📋 Requesting quotations for {item.name} (Qty: {quantity})")
        
        # Get relevant suppliers
        suppliers = await self.find_suitable_suppliers(item)
        
        if not suppliers:
            print(f"⚠️ No suitable suppliers found for {item.sku}")
            return []
        
        quotations = []
        
        for supplier in suppliers:
            try:
                # Send quotation request
                quotation = await self.send_quotation_request(supplier, item, quantity, urgency)
                if quotation:
                    quotations.append(quotation)
                    
            except Exception as e:
                print(f"❌ Error requesting quotation from {supplier.name}: {e}")
        
        # Store quotations
        self.price_quotations[item.sku] = quotations
        
        # Rank quotations by overall value
        ranked_quotations = await self.rank_quotations(quotations, item)
        
        print(f"✅ Received {len(quotations)} quotations for {item.name}")
        return ranked_quotations
    
    async def find_suitable_suppliers(self, item: InventoryItem) -> List[SupplierInfo]:
        """Find suppliers suitable for an item."""
        # Get all suppliers (this would be from database in real implementation)
        all_suppliers = await self.get_mock_suppliers()
        
        suitable_suppliers = []
        
        for supplier in all_suppliers:
            # Check if supplier handles this category
            if item.category in supplier.get('specialties', []):
                # Convert dict to SupplierInfo object for compatibility
                supplier_obj = SupplierInfo(
                    id=supplier['id'],
                    name=supplier['name'],
                    contact_email=supplier['contact_email'],
                    contact_phone=supplier.get('phone'),
                    reliability_score=supplier['rating'],
                    average_lead_time=supplier['delivery_time_days'],
                    min_order_quantity=supplier.get('min_order_quantity', 100)
                )
                suitable_suppliers.append(supplier_obj)
        
        # Sort by performance score
        return sorted(suitable_suppliers, 
                     key=lambda s: s.reliability_score, reverse=True)[:5]
    
    async def send_quotation_request(self, supplier: SupplierInfo, item: InventoryItem, 
                                   quantity: int, urgency: str) -> Optional[PriceQuotation]:
        """Send quotation request to supplier."""
        
        # Generate email content using AI
        email_content = await self.generate_quotation_email(supplier, item, quantity, urgency)
        
        # In real implementation, send actual email
        # For demo, we'll simulate supplier response
        await self.send_email(supplier.contact_email, email_content)
        
        # Simulate supplier response with realistic pricing
        quotation = await self.simulate_supplier_response(supplier, item, quantity)
        
        return quotation
    
    async def generate_quotation_email(self, supplier: SupplierInfo, item: InventoryItem, 
                                     quantity: int, urgency: str) -> Dict[str, str]:
        """Generate professional quotation request email using AI."""
        
        urgency_context = {
            "urgent": "We have an urgent requirement and need a quick response within 24 hours.",
            "normal": "Please provide your best quotation at your earliest convenience.",
            "bulk": "This is a bulk order inquiry with potential for regular business."
        }
        
        prompt = f"""
        Generate a professional quotation request email for:
        
        Supplier: {supplier.name}
        Item: {item.name} (SKU: {item.sku})
        Category: {item.category}
        Quantity: {quantity} units
        Urgency: {urgency}
        
        Context: {urgency_context.get(urgency, urgency_context['normal'])}
        
        Include:
        - Professional greeting
        - Clear product specifications
        - Quantity requirements
        - Request for pricing tiers
        - Delivery timeline inquiry
        - Payment terms discussion
        - Quality assurance requirements
        - Professional closing
        
        Make it business-friendly and encouraging for long-term partnership.
        """
        
        try:
            response = await self.gemini_client.generate_content(prompt)
            
            return {
                "subject": f"Quotation Request - {item.name} ({quantity} units)",
                "body": response.strip(),
                "priority": "high" if urgency == "urgent" else "normal"
            }
            
        except Exception as e:
            print(f"❌ Error generating email: {e}")
            # Fallback to template
            return self.get_fallback_email_template(supplier, item, quantity, urgency)
    
    def get_fallback_email_template(self, supplier: SupplierInfo, item: InventoryItem,
                                  quantity: int, urgency: str) -> Dict[str, str]:
        """Fallback email template."""
        
        body = f"""
        Dear {supplier.name} Team,
        
        We hope this email finds you well. We are reaching out to request a quotation for the following item:
        
        Product Details:
        - Item: {item.name}
        - SKU: {item.sku}
        - Category: {item.category}
        - Quantity Required: {quantity} units
        
        Please provide:
        1. Unit price for the specified quantity
        2. Bulk discount tiers (if applicable)
        3. Delivery timeline
        4. Payment terms
        5. Quality certifications
        
        We value long-term partnerships and look forward to your competitive quotation.
        
        Best regards,
        VeriChain Procurement Team
        procurement@verichain.com
        """
        
        return {
            "subject": f"Quotation Request - {item.name}",
            "body": body.strip(),
            "priority": "normal"
        }
    
    async def send_email(self, recipient: str, email_content: Dict[str, str]):
        """Send email to supplier (mock implementation)."""
        print(f"📧 Email sent to {recipient}")
        print(f"Subject: {email_content['subject']}")
        print(f"Preview: {email_content['body'][:100]}...")
        
        # In real implementation:
        # try:
        #     msg = MimeMultipart()
        #     msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['email']}>"
        #     msg['To'] = recipient
        #     msg['Subject'] = email_content['subject']
        #     
        #     msg.attach(MimeText(email_content['body'], 'plain'))
        #     
        #     server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        #     server.starttls()
        #     server.login(self.email_config['email'], self.email_config['password'])
        #     server.send_message(msg)
        #     server.quit()
        #     
        #     print(f"✅ Email sent successfully to {recipient}")
        # except Exception as e:
        #     print(f"❌ Email sending failed: {e}")
    
    async def simulate_supplier_response(self, supplier: SupplierInfo, item: InventoryItem,
                                       quantity: int) -> PriceQuotation:
        """Simulate realistic supplier response with pricing."""
        
        # Base price calculation with realistic variations
        base_price = item.unit_cost * random.uniform(0.8, 1.2)  # ±20% from cost
        
        # Supplier-specific adjustments
        reliability_factor = supplier.reliability_score / 10.0
        price_adjustment = 1.0 + (reliability_factor - 0.5) * 0.1  # ±5% based on reliability
        
        unit_price = base_price * price_adjustment
        
        # Generate discount tiers
        discount_tiers = {
            100: 0.0,    # No discount for minimum quantity
            500: 2.5,    # 2.5% for 500+
            1000: 5.0,   # 5% for 1000+
            2000: 7.5,   # 7.5% for 2000+
            5000: 10.0   # 10% for 5000+
        }
        
        # Apply current quantity discount
        applicable_discount = 0.0
        for qty_threshold, discount in sorted(discount_tiers.items()):
            if quantity >= qty_threshold:
                applicable_discount = discount
        
        final_unit_price = unit_price * (1 - applicable_discount / 100)
        
        return PriceQuotation(
            supplier_id=str(supplier.id),
            supplier_name=supplier.name,
            item_sku=item.sku,
            unit_price=final_unit_price,
            minimum_quantity=supplier.min_order_quantity,
            discount_tiers=discount_tiers,
            delivery_time=supplier.average_lead_time,
            payment_terms=f"Net {random.choice([15, 30, 45])}",
            validity_days=random.choice([7, 14, 21, 30]),
            special_conditions=[
                "Quality guarantee included",
                "Free delivery for orders above ₹10,000",
                "24/7 customer support"
            ],
            confidence_score=random.uniform(0.7, 0.95),
            created_at=datetime.utcnow()
        )
    
    async def rank_quotations(self, quotations: List[PriceQuotation], 
                            item: InventoryItem) -> List[PriceQuotation]:
        """Rank quotations based on multiple factors."""
        
        def calculate_score(quotation: PriceQuotation) -> float:
            score = 0.0
            
            # Price factor (40%)
            price_score = 1.0 / (quotation.unit_price / min(q.unit_price for q in quotations))
            score += price_score * 0.4
            
            # Delivery time factor (25%)
            delivery_score = 1.0 / (quotation.delivery_time / min(q.delivery_time for q in quotations))
            score += delivery_score * 0.25
            
            # Supplier reliability (20%)
            score += quotation.confidence_score * 0.2
            
            # Payment terms factor (10%)
            payment_days = int(quotation.payment_terms.split()[-1]) if "Net" in quotation.payment_terms else 30
            payment_score = 1.0 / (payment_days / 30.0)  # Normalized to 30 days
            score += payment_score * 0.1
            
            # Validity period factor (5%)
            validity_score = quotation.validity_days / 30.0  # Normalized to 30 days
            score += validity_score * 0.05
            
            return score
        
        # Sort by calculated score
        ranked = sorted(quotations, key=calculate_score, reverse=True)
        
        # Add ranking information
        for i, quotation in enumerate(ranked):
            quotation.rank = i + 1
            quotation.score = calculate_score(quotation)
        
        return ranked
    
    async def initiate_negotiation(self, quotation: PriceQuotation, target_price: float,
                                 max_rounds: int = 3) -> Dict[str, Any]:
        """Initiate AI-powered price negotiation with supplier."""
        
        print(f"🤝 Initiating negotiation with {quotation.supplier_name}")
        print(f"Initial quote: ₹{quotation.unit_price:.2f}, Target: ₹{target_price:.2f}")
        
        negotiation_id = f"{quotation.item_sku}_{quotation.supplier_id}_{int(datetime.now().timestamp())}"
        self.active_negotiations[negotiation_id] = []
        
        # Calculate negotiation strategy
        strategy = await self.plan_negotiation_strategy(quotation, target_price)
        
        current_round = 1
        current_offer = quotation.unit_price
        
        while current_round <= max_rounds:
            # Generate our counter-offer
            our_offer = await self.generate_counter_offer(
                quotation, target_price, current_round, max_rounds, strategy
            )
            
            # Generate justification for our offer
            justification = await self.generate_negotiation_justification(
                quotation, our_offer, current_round, strategy
            )
            
            # Simulate supplier response
            supplier_response = await self.simulate_supplier_counter_offer(
                quotation, our_offer, current_round, max_rounds
            )
            
            # Create negotiation round
            round_data = NegotiationRound(
                round_number=current_round,
                our_offer=our_offer,
                supplier_response=supplier_response['price'],
                our_justification=justification,
                supplier_justification=supplier_response['justification'],
                status=NegotiationStatus.from_string(supplier_response['status']),
                timestamp=datetime.utcnow()
            )
            
            self.active_negotiations[negotiation_id].append(round_data)
            
            print(f"Round {current_round}: Our offer ₹{our_offer:.2f} → Supplier response ₹{supplier_response['price']:.2f}")
            
            # Check if negotiation concluded
            if supplier_response['status'] == 'agreed':
                final_result = {
                    "status": "success",
                    "final_price": supplier_response['price'],
                    "savings": quotation.unit_price - supplier_response['price'],
                    "rounds": current_round,
                    "negotiation_id": negotiation_id
                }
                
                await self.finalize_negotiation(negotiation_id, final_result)
                return final_result
            
            elif supplier_response['status'] == 'rejected':
                final_result = {
                    "status": "failed",
                    "reason": "Supplier rejected final offer",
                    "best_price": min(r.supplier_response for r in self.active_negotiations[negotiation_id]),
                    "rounds": current_round,
                    "negotiation_id": negotiation_id
                }
                
                await self.finalize_negotiation(negotiation_id, final_result)
                return final_result
            
            current_offer = supplier_response['price']
            current_round += 1
        
        # Max rounds reached
        best_price = min(r.supplier_response for r in self.active_negotiations[negotiation_id])
        final_result = {
            "status": "partial_success",
            "final_price": best_price,
            "savings": quotation.unit_price - best_price,
            "rounds": max_rounds,
            "negotiation_id": negotiation_id,
            "reason": "Maximum negotiation rounds reached"
        }
        
        await self.finalize_negotiation(negotiation_id, final_result)
        return final_result
    
    async def plan_negotiation_strategy(self, quotation: PriceQuotation, 
                                      target_price: float) -> Dict[str, Any]:
        """Plan AI-powered negotiation strategy."""
        
        # Calculate negotiation room
        price_gap = quotation.unit_price - target_price
        price_gap_percentage = (price_gap / quotation.unit_price) * 100
        
        # Determine strategy based on gap
        if price_gap_percentage <= 5:
            strategy_type = "gentle"
        elif price_gap_percentage <= 15:
            strategy_type = "moderate"
        else:
            strategy_type = "aggressive"
        
        # Generate strategy points
        strategy_points = []
        
        if quotation.delivery_time > 7:
            strategy_points.append("Highlight our quick payment terms")
        
        if price_gap_percentage > 10:
            strategy_points.append("Emphasize long-term partnership potential")
            strategy_points.append("Mention bulk order commitments")
        
        strategy_points.append("Compare with market rates")
        strategy_points.append("Highlight our business reliability")
        
        return {
            "type": strategy_type,
            "target_reduction": price_gap_percentage,
            "key_points": strategy_points,
            "max_concession_per_round": price_gap / 3,  # Spread reduction over 3 rounds
            "opening_offer_percentage": 70 if strategy_type == "aggressive" else 85
        }
    
    async def generate_counter_offer(self, quotation: PriceQuotation, target_price: float,
                                   current_round: int, max_rounds: int, 
                                   strategy: Dict[str, Any]) -> float:
        """Generate AI-optimized counter-offer."""
        
        if current_round == 1:
            # Opening offer
            opening_percentage = strategy["opening_offer_percentage"] / 100
            return target_price + (quotation.unit_price - target_price) * (1 - opening_percentage)
        
        # Subsequent rounds - gradually approach target
        progress = current_round / max_rounds
        remaining_gap = quotation.unit_price - target_price
        
        # Non-linear progression (more aggressive towards the end)
        progress_factor = progress ** 1.5
        
        return quotation.unit_price - (remaining_gap * progress_factor)
    
    async def generate_negotiation_justification(self, quotation: PriceQuotation,
                                               our_offer: float, round_number: int,
                                               strategy: Dict[str, Any]) -> str:
        """Generate AI-powered negotiation justification."""
        
        justifications = []
        
        if round_number == 1:
            justifications.append(f"Based on current market rates and our bulk requirement")
            justifications.append(f"We value long-term partnerships with reliable suppliers")
        
        reduction_percentage = ((quotation.unit_price - our_offer) / quotation.unit_price) * 100
        
        if reduction_percentage > 5:
            justifications.append(f"This pricing aligns with our budget constraints")
            justifications.append(f"We offer quick payment and repeat business")
        
        if strategy["type"] == "aggressive":
            justifications.append(f"We have competitive quotes from other suppliers")
        
        justifications.append(f"This price point ensures mutual benefit and sustainability")
        
        return "; ".join(justifications)
    
    async def simulate_supplier_counter_offer(self, quotation: PriceQuotation,
                                            our_offer: float, round_number: int,
                                            max_rounds: int) -> Dict[str, Any]:
        """Simulate realistic supplier counter-offer."""
        
        # Supplier's willingness to negotiate (based on their margin)
        estimated_cost = quotation.unit_price * 0.7  # Assume 30% margin
        minimum_acceptable = estimated_cost * 1.1    # 10% minimum margin
        
        reduction_requested = quotation.unit_price - our_offer
        max_possible_reduction = quotation.unit_price - minimum_acceptable
        
        # Supplier behavior simulation
        if our_offer < minimum_acceptable:
            # Reject if below minimum
            return {
                "price": quotation.unit_price,
                "status": "rejected",
                "justification": "Price below our minimum acceptable margin"
            }
        
        elif reduction_requested <= max_possible_reduction * 0.6:
            # Accept if within reasonable range
            final_price = our_offer + random.uniform(0, reduction_requested * 0.1)
            return {
                "price": final_price,
                "status": "agreed",
                "justification": f"Agreed for long-term partnership potential"
            }
        
        else:
            # Counter-offer in between
            if round_number >= max_rounds:
                # Last round - more likely to agree or reject
                if random.random() > 0.3:  # 70% chance of agreement
                    final_price = minimum_acceptable + random.uniform(0, max_possible_reduction * 0.2)
                    return {
                        "price": final_price,
                        "status": "agreed",
                        "justification": "Final offer considering all factors"
                    }
                else:
                    return {
                        "price": quotation.unit_price,
                        "status": "rejected",
                        "justification": "Unable to meet requested pricing"
                    }
            else:
                # Intermediate round - make counter-offer
                counter_price = our_offer + (quotation.unit_price - our_offer) * random.uniform(0.3, 0.7)
                return {
                    "price": counter_price,
                    "status": "counter_offer",
                    "justification": f"Counter-offer considering volume and partnership value"
                }
    
    async def finalize_negotiation(self, negotiation_id: str, result: Dict[str, Any]):
        """Finalize negotiation and notify stakeholders."""
        
        # Save negotiation to database (mock)
        print(f"💾 Saving negotiation {negotiation_id}: {result['status']}")
        
        # Send notification
        if result['status'] == 'success':
            message = f"Negotiation successful! Final price: ₹{result['final_price']:.2f}, Savings: ₹{result['savings']:.2f}"
        else:
            message = f"Negotiation {result['status']}: {result.get('reason', 'See details')}"
        
        await notification_manager.send_notification(
            type="negotiation_complete",
            title=f"Negotiation {result['status'].title()}",
            message=message,
            recipient="procurement@verichain.com"
        )
    
    async def get_mock_suppliers(self) -> List[Dict[str, Any]]:
        """Get mock supplier data (replace with database query)."""
        return [
            {
                "id": "supplier_001",
                "name": "Rajesh Stationery Wholesale",
                "contact_email": "rajesh@rswholesale.com",
                "phone": "+91-9876543210",
                "specialties": ["WRITING_INSTRUMENTS", "PAPER_NOTEBOOKS"],
                "rating": 4.5,
                "delivery_time_days": 3,
                "min_order_quantity": 100
            },
            {
                "id": "supplier_002",
                "name": "Modern Office Solutions",
                "contact_email": "orders@modernofficeindia.com",
                "phone": "+91-9876543211",
                "specialties": ["OFFICE_SUPPLIES", "BAGS_STORAGE"],
                "rating": 4.2,
                "delivery_time_days": 5,
                "min_order_quantity": 50
            },
            {
                "id": "supplier_003",
                "name": "Creative Arts Suppliers",
                "contact_email": "sales@creativeartsupply.in",
                "phone": "+91-9876543212",
                "specialties": ["ART_CRAFT"],
                "rating": 4.7,
                "delivery_time_days": 7,
                "min_order_quantity": 25
            }
        ]
    
    # API Methods for Dashboard Integration
    
    async def get_active_negotiations(self) -> List[Dict[str, Any]]:
        """Get all active negotiations."""
        active = []
        
        for negotiation_id, rounds in self.active_negotiations.items():
            if rounds:
                latest_round = rounds[-1]
                active.append({
                    "negotiation_id": negotiation_id,
                    "supplier_name": negotiation_id.split('_')[1],  # Extract supplier from ID
                    "item_sku": negotiation_id.split('_')[0],
                    "current_round": latest_round.round_number,
                    "latest_offer": latest_round.our_offer,
                    "supplier_response": latest_round.supplier_response,
                    "status": latest_round.status.value,
                    "last_activity": latest_round.timestamp.isoformat()
                })
        
        return active
    
    async def get_quotation_comparison(self, item_sku: str) -> Dict[str, Any]:
        """Get quotation comparison for an item."""
        quotations = self.price_quotations.get(item_sku, [])
        
        if not quotations:
            return {"error": "No quotations available"}
        
        return {
            "item_sku": item_sku,
            "quotation_count": len(quotations),
            "best_price": min(q.unit_price for q in quotations),
            "worst_price": max(q.unit_price for q in quotations),
            "avg_delivery_time": sum(q.delivery_time for q in quotations) / len(quotations),
            "quotations": [
                {
                    "supplier_name": q.supplier_name,
                    "unit_price": q.unit_price,
                    "delivery_time": q.delivery_time,
                    "payment_terms": q.payment_terms,
                    "discount_tiers": q.discount_tiers,
                    "confidence_score": q.confidence_score
                }
                for q in quotations
            ]
        }

# Global supplier manager instance
supplier_manager = None

async def initialize_supplier_manager(gemini_client: GeminiClient):
    """Initialize the supplier manager."""
    global supplier_manager
    supplier_manager = SupplierManager(gemini_client)
    print("🏪 Supplier management system initialized")

async def get_supplier_manager() -> SupplierManager:
    """Get the supplier manager instance."""
    return supplier_manager