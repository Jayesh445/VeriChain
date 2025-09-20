"""
Base agent classes and utilities for VeriChain.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from loguru import logger

from app.models import (
    AgentRole, AgentDecision, ActionType, Priority, InventoryItem, 
    SalesData, SupplierInfo, AgentConfig, AgentMemory
)
from app.services.gemini_client import GeminiClient


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the VeriChain system.
    """
    
    def __init__(
        self,
        agent_role: AgentRole,
        gemini_client: GeminiClient,
        config: Optional[AgentConfig] = None
    ):
        self.agent_role = agent_role
        self.gemini_client = gemini_client
        self.config = config or AgentConfig()
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            k=self.config.memory_size
        )
        self.conversation_id = uuid4()
        
        logger.info(f"Initialized {self.agent_role} agent with conversation ID: {self.conversation_id}")
    
    @abstractmethod
    def get_system_instruction(self) -> str:
        """Get the system instruction for this agent role."""
        pass
    
    @abstractmethod
    def build_context_prompt(
        self,
        inventory_data: List[InventoryItem],
        sales_data: Optional[List[SalesData]] = None,
        supplier_data: Optional[List[SupplierInfo]] = None,
        user_query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the context-specific prompt for this agent."""
        pass
    
    @abstractmethod
    def parse_decision(self, response: str) -> List[AgentDecision]:
        """Parse the agent's response into structured decisions."""
        pass
    
    def add_to_memory(self, human_message: str, ai_message: str) -> None:
        """Add messages to conversation memory."""
        self.memory.chat_memory.add_user_message(human_message)
        self.memory.chat_memory.add_ai_message(ai_message)
    
    def get_memory_context(self) -> str:
        """Get formatted memory context for prompt."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No previous conversation history."
        
        context_lines = []
        for message in messages[-self.config.memory_size:]:
            if isinstance(message, HumanMessage):
                context_lines.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                context_lines.append(f"Agent: {message.content}")
        
        return "\n".join(context_lines)
    
    def _format_inventory_data(self, inventory_data: List[InventoryItem]) -> str:
        """Format inventory data for prompt."""
        if not inventory_data:
            return "No inventory data available."
        
        lines = ["INVENTORY DATA:"]
        for item in inventory_data:
            status_indicator = "⚠️" if item.status.value == "low_stock" else "❌" if item.status.value == "out_of_stock" else "✅"
            lines.append(
                f"{status_indicator} SKU: {item.sku} | {item.name} | "
                f"Stock: {item.current_stock}/{item.max_stock_capacity} | "
                f"Min Threshold: {item.min_stock_threshold} | "
                f"Category: {item.category} | "
                f"Unit Cost: ${item.unit_cost:.2f} | "
                f"Lead Time: {item.lead_time_days} days"
            )
        
        return "\n".join(lines)
    
    def _format_sales_data(self, sales_data: Optional[List[SalesData]]) -> str:
        """Format sales data for prompt."""
        if not sales_data:
            return "No sales data available."
        
        lines = ["SALES DATA (Recent):"]
        # Sort by date and take recent entries
        sorted_sales = sorted(sales_data, key=lambda x: x.date, reverse=True)[:20]
        
        for sale in sorted_sales:
            lines.append(
                f"SKU: {sale.sku} | "
                f"Date: {sale.date.strftime('%Y-%m-%d')} | "
                f"Sold: {sale.quantity_sold} units | "
                f"Revenue: ${sale.revenue:.2f} | "
                f"Channel: {sale.channel}"
            )
        
        return "\n".join(lines)
    
    def _format_supplier_data(self, supplier_data: Optional[List[SupplierInfo]]) -> str:
        """Format supplier data for prompt."""
        if not supplier_data:
            return "No supplier data available."
        
        lines = ["SUPPLIER DATA:"]
        for supplier in supplier_data:
            reliability_stars = "⭐" * min(int(supplier.reliability_score), 5)
            lines.append(
                f"Supplier: {supplier.name} | "
                f"Reliability: {reliability_stars} ({supplier.reliability_score}/10) | "
                f"Lead Time: {supplier.average_lead_time} days | "
                f"Min Order: {supplier.min_order_quantity} units"
            )
        
        return "\n".join(lines)
    
    async def act(
        self,
        inventory_data: List[InventoryItem],
        sales_data: Optional[List[SalesData]] = None,
        supplier_data: Optional[List[SupplierInfo]] = None,
        user_query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[AgentDecision]:
        """
        Main action method for the agent.
        
        Args:
            inventory_data: Current inventory information
            sales_data: Historical sales data
            supplier_data: Supplier information
            user_query: Optional user query or instruction
            context: Additional context information
            
        Returns:
            List of agent decisions
        """
        start_time = datetime.utcnow()
        
        try:
            # Build the complete prompt
            context_prompt = self.build_context_prompt(
                inventory_data=inventory_data,
                sales_data=sales_data,
                supplier_data=supplier_data,
                user_query=user_query,
                context=context
            )
            
            # Get system instruction
            system_instruction = self.get_system_instruction()
            
            # Add memory context
            memory_context = self.get_memory_context()
            if memory_context != "No previous conversation history.":
                context_prompt = f"CONVERSATION HISTORY:\n{memory_context}\n\n{context_prompt}"
            
            logger.info(f"Generating decision for {self.agent_role} agent")
            
            # Generate response using Gemini
            response = await self.gemini_client.generate_text(
                prompt=context_prompt,
                system_instruction=system_instruction
            )
            
            # Parse decisions from response
            decisions = self.parse_decision(response)
            
            # Add to memory
            self.add_to_memory(
                human_message=user_query or "Analyze current situation and provide recommendations",
                ai_message=response
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"Agent {self.agent_role} completed analysis in {processing_time:.2f}s, "
                f"generated {len(decisions)} decisions"
            )
            
            return decisions
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(
                f"Agent {self.agent_role} failed after {processing_time:.2f}s: {str(e)}"
            )
            raise
    
    def get_memory_summary(self) -> AgentMemory:
        """Get a summary of the agent's memory."""
        messages = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                messages.append({"role": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                messages.append({"role": "agent", "content": message.content})
        
        return AgentMemory(
            conversation_id=self.conversation_id,
            messages=messages,
            context={"agent_role": self.agent_role.value}
        )