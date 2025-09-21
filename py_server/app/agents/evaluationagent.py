"""
Evaluation Agent for processing offers and selecting optimal deal
"""

import numpy as np
from typing import List, Dict, Any

class EvaluationAgent:
    def __init__(self):
        # Weights for decision matrix (customize based on priorities)
        self.weights = {
            "price": 0.4,
            "delivery": 0.25,
            "reliability": 0.2,
            "past_performance": 0.15
        }
    
    def evaluate_offers(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate offers using a decision matrix"""
        evaluated_offers = []
        
        for offer in offers:
            current = offer["current_offer"]
            score = self._calculate_score(
                current["price"],
                current["delivery_days"],
                current["reliability_score"],
                current["past_performance"]
            )
            
            evaluated_offer = offer.copy()
            evaluated_offer["evaluation_score"] = round(score, 4)
            evaluated_offers.append(evaluated_offer)
        
        # Sort by evaluation score (descending)
        evaluated_offers.sort(key=lambda x: x["evaluation_score"], reverse=True)
        
        return evaluated_offers
    
    def select_optimal_deal(self, evaluated_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the optimal deal based on evaluation scores"""
        if not evaluated_offers:
            raise ValueError("No offers to evaluate")
        
        # Find offer with highest score
        optimal_offer = evaluated_offers[0]
        
        # Add evaluation metadata
        optimal_offer["evaluation_metadata"] = {
            "evaluation_date": "2024-01-01",  # Would use datetime in real implementation
            "criteria_weights": self.weights,
            "rank": 1,
            "total_offers": len(evaluated_offers)
        }
        
        return optimal_offer
    
    def _calculate_score(self, price: float, delivery_days: int, reliability: float, past_performance: float) -> float:
        """Calculate weighted score for an offer"""
        # Normalize values (lower price and delivery days are better)
        normalized_price = 1 / (price / 10000)  # Reference value
        normalized_delivery = 1 / (delivery_days / 30)  # Reference value
        
        # Calculate weighted score
        score = (
            self.weights["price"] * normalized_price +
            self.weights["delivery"] * normalized_delivery +
            self.weights["reliability"] * reliability / 5.0 +  # Scale to 0-1
            self.weights["past_performance"] * past_performance / 5.0  # Scale to 0-1
        )
        
        return score
    
    def create_hybrid_deal(self, top_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a hybrid deal combining the best aspects of multiple offers"""
        if len(top_offers) < 2:
            return top_offers[0] if top_offers else None
        
        # For demonstration, just return the best offer
        # In a real implementation, this would combine terms from multiple vendors
        return top_offers[0]