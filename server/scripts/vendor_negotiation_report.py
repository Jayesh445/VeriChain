#!/usr/bin/env python3
"""
Vendor Negotiation Report Generator
Creates comprehensive reports with profit analysis and Excel export functionality
"""

import asyncio
import pandas as pd
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
import random
import os

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import Vendor, StationeryItem, Order, VendorStatus


class VendorNegotiationReportGenerator:
    """Generate comprehensive vendor negotiation reports with Excel export"""
    
    def __init__(self):
        self.mock_data = []
        self.profit_analysis = None
        
    async def generate_mock_negotiation_data(self, db: AsyncSession, num_negotiations: int = 10) -> List[Dict]:
        """Generate mock negotiation data for demonstration"""
        
        # Get real vendors and items
        vendors_result = await db.execute(select(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).limit(5))
        vendors = vendors_result.scalars().all()
        
        items_result = await db.execute(select(StationeryItem).limit(10))
        items = items_result.scalars().all()
        
        if not vendors or not items:
            print("No vendors or items found. Creating sample data...")
            return self._create_sample_data()
        
        negotiations = []
        
        for i in range(num_negotiations):
            item = random.choice(items)
            vendor = random.choice(vendors)
            
            # Generate realistic negotiation data
            base_cost = random.uniform(5, 15)  # Cost price
            profit_margin = random.uniform(0.15, 0.50)  # 15-50% margin
            unit_price = base_cost * (1 + profit_margin)
            quantity = random.randint(50, 500)
            
            # Negotiation phases
            phases = ["discovery", "initial_offer", "negotiation", "counter_offer", "final_agreement"]
            
            negotiation = {
                "negotiation_id": f"NEG-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                "item_id": item.id,
                "item_name": item.name,
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "quantity": quantity,
                "base_cost": round(base_cost, 2),
                "initial_offer": round(unit_price * 1.1, 2),  # Start 10% higher
                "final_price": round(unit_price, 2),
                "total_value": round(unit_price * quantity, 2),
                "profit_margin": round(profit_margin * 100, 2),
                "profit_amount": round((unit_price - base_cost) * quantity, 2),
                "delivery_days": random.randint(3, 21),
                "negotiation_rounds": random.randint(2, 6),
                "savings_achieved": round(unit_price * 0.1 * quantity, 2),  # 10% savings
                "confidence_score": random.uniform(0.75, 0.98),
                "special_terms": random.choice([
                    "Free shipping", "Extended warranty", "Bulk discount", 
                    "Early payment discount", "Priority support", None
                ]),
                "negotiation_date": datetime.now() - timedelta(days=random.randint(0, 30)),
                "status": random.choice(["completed", "approved", "pending"]),
                "ai_reasoning": f"Selected {vendor.name} based on competitive pricing and reliable delivery terms",
                "phases": phases
            }
            
            negotiations.append(negotiation)
        
        self.mock_data = negotiations
        return negotiations
    
    def _create_sample_data(self) -> List[Dict]:
        """Create sample data when no database items exist"""
        vendors = [
            {"id": 1, "name": "Office Supply Pro"},
            {"id": 2, "name": "Business Essentials Ltd"},
            {"id": 3, "name": "Stationery World Inc"},
            {"id": 4, "name": "Corporate Supplies Co"}
        ]
        
        items = [
            {"id": 1, "name": "A4 Copy Paper"},
            {"id": 2, "name": "Black Ink Pens"},
            {"id": 3, "name": "Stapler Standard"},
            {"id": 4, "name": "Sticky Notes Yellow"},
            {"id": 5, "name": "File Folders Manila"}
        ]
        
        negotiations = []
        for i in range(10):
            vendor = random.choice(vendors)
            item = random.choice(items)
            
            base_cost = random.uniform(5, 15)
            profit_margin = random.uniform(0.15, 0.50)
            unit_price = base_cost * (1 + profit_margin)
            quantity = random.randint(50, 500)
            
            negotiation = {
                "negotiation_id": f"NEG-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                "item_id": item["id"],
                "item_name": item["name"],
                "vendor_id": vendor["id"], 
                "vendor_name": vendor["name"],
                "quantity": quantity,
                "base_cost": round(base_cost, 2),
                "initial_offer": round(unit_price * 1.1, 2),
                "final_price": round(unit_price, 2),
                "total_value": round(unit_price * quantity, 2),
                "profit_margin": round(profit_margin * 100, 2),
                "profit_amount": round((unit_price - base_cost) * quantity, 2),
                "delivery_days": random.randint(3, 21),
                "negotiation_rounds": random.randint(2, 6),
                "savings_achieved": round(unit_price * 0.1 * quantity, 2),
                "confidence_score": random.uniform(0.75, 0.98),
                "special_terms": random.choice([
                    "Free shipping", "Extended warranty", "Bulk discount",
                    "Early payment discount", "Priority support", None
                ]),
                "negotiation_date": datetime.now() - timedelta(days=random.randint(0, 30)),
                "status": random.choice(["completed", "approved", "pending"]),
                "ai_reasoning": f"Selected {vendor['name']} based on competitive pricing and reliable delivery terms"
            }
            
            negotiations.append(negotiation)
        
        self.mock_data = negotiations
        return negotiations
    
    def analyze_vendor_performance(self) -> pd.DataFrame:
        """Analyze vendor performance and generate profit metrics"""
        
        if not self.mock_data:
            raise ValueError("No negotiation data available. Generate mock data first.")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.mock_data)
        
        # Vendor performance analysis
        vendor_analysis = df.groupby(['vendor_id', 'vendor_name']).agg({
            'total_value': ['sum', 'mean', 'count'],
            'profit_amount': ['sum', 'mean'],
            'profit_margin': 'mean',
            'delivery_days': 'mean',
            'confidence_score': 'mean',
            'savings_achieved': 'sum',
            'negotiation_rounds': 'mean'
        }).round(2)
        
        # Flatten column names
        vendor_analysis.columns = [
            'Total_Revenue', 'Avg_Order_Value', 'Order_Count',
            'Total_Profit', 'Avg_Profit_Per_Order', 'Avg_Profit_Margin',
            'Avg_Delivery_Days', 'Avg_Confidence', 'Total_Savings',
            'Avg_Negotiation_Rounds'
        ]
        
        # Calculate performance scores
        vendor_analysis['Performance_Score'] = (
            (vendor_analysis['Avg_Confidence'] * 0.3) +
            (vendor_analysis['Avg_Profit_Margin'] / 100 * 0.3) +
            ((21 - vendor_analysis['Avg_Delivery_Days']) / 21 * 0.2) +
            ((10 - vendor_analysis['Avg_Negotiation_Rounds']) / 10 * 0.2)
        ).round(3)
        
        # Reset index to make vendor columns accessible
        vendor_analysis = vendor_analysis.reset_index()
        
        self.profit_analysis = vendor_analysis
        return vendor_analysis
    
    def create_pivot_summary(self) -> pd.DataFrame:
        """Create pivot table summary of negotiations"""
        
        if not self.mock_data:
            raise ValueError("No negotiation data available.")
        
        df = pd.DataFrame(self.mock_data)
        
        # Create pivot table
        pivot = pd.pivot_table(
            df,
            values=['total_value', 'profit_amount', 'savings_achieved'],
            index=['vendor_name'],
            columns=['status'],
            aggfunc='sum',
            fill_value=0
        ).round(2)
        
        return pivot
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export comprehensive report to Excel file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vendor_negotiation_report_{timestamp}.xlsx"
        
        # Ensure the reports directory exists
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: Raw negotiation data
            if self.mock_data:
                negotiations_df = pd.DataFrame(self.mock_data)
                negotiations_df.to_excel(writer, sheet_name='Negotiations', index=False)
            
            # Sheet 2: Vendor performance analysis
            if self.profit_analysis is not None:
                self.profit_analysis.to_excel(writer, sheet_name='Vendor_Analysis', index=False)
            
            # Sheet 3: Pivot summary
            if self.mock_data:
                pivot_summary = self.create_pivot_summary()
                pivot_summary.to_excel(writer, sheet_name='Pivot_Summary')
            
            # Sheet 4: Executive summary
            self._create_executive_summary(writer)
        
        return filepath
    
    def _create_executive_summary(self, writer):
        """Create an executive summary sheet"""
        
        if not self.mock_data or self.profit_analysis is None:
            return
        
        # Calculate summary metrics
        total_negotiations = len(self.mock_data)
        total_revenue = sum(neg['total_value'] for neg in self.mock_data)
        total_profit = sum(neg['profit_amount'] for neg in self.mock_data)
        avg_profit_margin = sum(neg['profit_margin'] for neg in self.mock_data) / total_negotiations
        total_savings = sum(neg['savings_achieved'] for neg in self.mock_data)
        
        # Best performing vendor
        best_vendor = self.profit_analysis.loc[
            self.profit_analysis['Performance_Score'].idxmax()
        ]
        
        summary_data = {
            'Metric': [
                'Total Negotiations',
                'Total Revenue ($)',
                'Total Profit ($)',
                'Average Profit Margin (%)',
                'Total Savings Achieved ($)',
                'Best Performing Vendor',
                'Best Vendor Performance Score',
                'Report Generated'
            ],
            'Value': [
                total_negotiations,
                f"${total_revenue:,.2f}",
                f"${total_profit:,.2f}",
                f"{avg_profit_margin:.2f}%",
                f"${total_savings:,.2f}",
                best_vendor['vendor_name'],
                f"{best_vendor['Performance_Score']:.3f}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
    
    def print_summary(self):
        """Print a summary of the analysis to console"""
        
        if not self.mock_data:
            print("No data available for summary.")
            return
        
        print("\n" + "="*60)
        print("VENDOR NEGOTIATION ANALYSIS SUMMARY")
        print("="*60)
        
        total_negotiations = len(self.mock_data)
        total_revenue = sum(neg['total_value'] for neg in self.mock_data)
        total_profit = sum(neg['profit_amount'] for neg in self.mock_data)
        avg_profit_margin = sum(neg['profit_margin'] for neg in self.mock_data) / total_negotiations
        
        print(f"Total Negotiations: {total_negotiations}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Profit: ${total_profit:,.2f}")
        print(f"Average Profit Margin: {avg_profit_margin:.2f}%")
        
        if self.profit_analysis is not None:
            print("\nTOP PERFORMING VENDORS:")
            print("-"*40)
            top_vendors = self.profit_analysis.nlargest(3, 'Performance_Score')
            for idx, vendor in top_vendors.iterrows():
                print(f"{vendor['vendor_name']}: Score {vendor['Performance_Score']:.3f}")
                print(f"  - Total Revenue: ${vendor['Total_Revenue']:,.2f}")
                print(f"  - Avg Profit Margin: {vendor['Avg_Profit_Margin']:.2f}%")
                print(f"  - Avg Delivery: {vendor['Avg_Delivery_Days']:.1f} days")
                print()


async def main():
    """Main function to run the report generator"""
    
    print("Starting Vendor Negotiation Report Generation...")
    
    generator = VendorNegotiationReportGenerator()
    
    # Generate mock data
    async with AsyncSessionLocal() as db:
        negotiations = await generator.generate_mock_negotiation_data(db, num_negotiations=15)
    
    print(f"Generated {len(negotiations)} mock negotiations")
    
    # Analyze vendor performance
    vendor_analysis = generator.analyze_vendor_performance()
    print("Completed vendor performance analysis")
    
    # Export to Excel
    excel_file = generator.export_to_excel()
    print(f"Excel report exported to: {excel_file}")
    
    # Print summary
    generator.print_summary()
    
    print("\nReport generation completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())