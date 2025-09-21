"""
Smart Contract Manager for drafting Solidity contracts
"""

from typing import Dict, Any
from datetime import datetime, timedelta

class ContractManager:
    def __init__(self):
        self.contract_template = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        contract VendorAgreement {
            address public buyer;
            address public vendor;
            string public vendorName;
            uint256 public contractValue;
            uint256 public deliveryDate;
            uint256 public reliabilityScore;
            uint256 public pastPerformanceScore;
            string public paymentTerms;
            string public warrantyTerms;
            bool public fulfilled;
            bool public disputed;
            
            event AgreementCreated(
                address indexed buyer,
                address indexed vendor,
                uint256 value,
                uint256 deliveryDate
            );
            
            event AgreementFulfilled(address indexed vendor, uint256 fulfilledDate);
            event DisputeRaised(address indexed raisedBy, string reason);
            
            constructor(
                address _vendor,
                string memory _vendorName,
                uint256 _contractValue,
                uint256 _deliveryDays,
                uint256 _reliabilityScore,
                uint256 _pastPerformanceScore,
                string memory _paymentTerms,
                string memory _warrantyTerms
            ) {
                buyer = msg.sender;
                vendor = _vendor;
                vendorName = _vendorName;
                contractValue = _contractValue;
                deliveryDate = block.timestamp + (_deliveryDays * 1 days);
                reliabilityScore = _reliabilityScore;
                pastPerformanceScore = _pastPerformanceScore;
                paymentTerms = _paymentTerms;
                warrantyTerms = _warrantyTerms;
                fulfilled = false;
                disputed = false;
                
                emit AgreementCreated(buyer, vendor, contractValue, deliveryDate);
            }
            
            function markFulfilled() public {
                require(msg.sender == buyer, "Only buyer can mark as fulfilled");
                require(!fulfilled, "Agreement already fulfilled");
                require(!disputed, "Agreement is disputed");
                
                fulfilled = true;
                emit AgreementFulfilled(vendor, block.timestamp);
            }
            
            function raiseDispute(string memory reason) public {
                require(msg.sender == buyer || msg.sender == vendor, "Only parties can raise dispute");
                require(!fulfilled, "Agreement already fulfilled");
                require(!disputed, "Dispute already raised");
                
                disputed = true;
                emit DisputeRaised(msg.sender, reason);
            }
            
            function getAgreementDetails() public view returns (
                address, address, string memory, uint256, uint256, uint256, uint256, string memory, string memory, bool, bool
            ) {
                return (
                    buyer,
                    vendor,
                    vendorName,
                    contractValue,
                    deliveryDate,
                    reliabilityScore,
                    pastPerformanceScore,
                    paymentTerms,
                    warrantyTerms,
                    fulfilled,
                    disputed
                );
            }
        }
        """
    
    def draft_smart_contract(self, deal: Dict[str, Any]) -> str:
        """Draft a Solidity smart contract based on the negotiated deal"""
        # Extract relevant information from the deal
        current_offer = deal["current_offer"]
        
        # In a real implementation, you would use template rendering with actual values
        # For this example, we return the template as-is with some placeholder replacement
        contract_code = self.contract_template
        
        # Simple placeholder replacement (in real implementation, use proper templating)
        contract_code = contract_code.replace("_vendorName", deal["vendor_name"])
        contract_code = contract_code.replace("_contractValue", str(int(current_offer["price"])))
        contract_code = contract_code.replace("_deliveryDays", str(current_offer["delivery_days"]))
        contract_code = contract_code.replace("_reliabilityScore", str(int(current_offer["reliability_score"] * 10)))
        contract_code = contract_code.replace("_pastPerformanceScore", str(int(current_offer["past_performance"] * 10)))
        
        # Add metadata comment
        metadata_comment = f"""
        // Contract generated for {deal['vendor_name']}
        // Negotiation completed on {datetime.now().isoformat()}
        // Total value: ${current_offer['price']:,.2f}
        """
        
        return metadata_comment + contract_code