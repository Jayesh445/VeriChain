"""
LangChain integration with Google Gemini for VeriChain agents.
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from loguru import logger

from app.core.config import settings


class AgentDecisionOutput(BaseModel):
    """Pydantic model for agent decision output parsing."""
    decisions: List[Dict[str, Any]] = Field(description="List of agent decisions")
    summary: str = Field(description="Summary of the analysis")
    confidence_score: float = Field(description="Overall confidence score", ge=0.0, le=1.0)
    next_actions: Optional[List[str]] = Field(description="Suggested next actions")


class LangChainGeminiAgent:
    """
    LangChain-based agent using Google Gemini for stationery inventory management.
    """
    
    def __init__(
        self,
        agent_role: str,
        system_prompt: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.2,
        memory_window: int = 10
    ):
        self.agent_role = agent_role
        self.system_prompt = system_prompt
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.google_api_key,
            convert_system_message_to_human=True
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Initialize output parser
        self.output_parser = PydanticOutputParser(pydantic_object=AgentDecisionOutput)
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + "\n\nFormat your response according to this schema:\n{format_instructions}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create the chain
        self.chain = self.prompt_template | self.llm | self.output_parser
        
        logger.info(f"Initialized LangChain Gemini agent for role: {agent_role}")
    
    async def arun(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentDecisionOutput:
        """
        Run the agent asynchronously.
        
        Args:
            input_data: The input prompt/data for the agent
            context: Additional context information
            
        Returns:
            Parsed agent decision output
        """
        try:
            # Get chat history from memory
            chat_history = self.memory.chat_memory.messages
            
            # Prepare the input
            chain_input = {
                "input": input_data,
                "chat_history": chat_history,
                "format_instructions": self.output_parser.get_format_instructions()
            }
            
            logger.info(f"Running {self.agent_role} agent with LangChain")
            start_time = datetime.utcnow()
            
            # Invoke the chain
            result = await self.chain.ainvoke(chain_input)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add to memory
            self.memory.chat_memory.add_user_message(input_data)
            self.memory.chat_memory.add_ai_message(str(result))
            
            logger.info(f"Agent {self.agent_role} completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running agent {self.agent_role}: {str(e)}")
            # Return fallback response
            return AgentDecisionOutput(
                decisions=[{
                    "item_sku": "ERROR",
                    "action_type": "alert",
                    "priority": "medium",
                    "confidence_score": 0.1,
                    "reasoning": f"Error in agent processing: {str(e)}",
                    "recommended_quantity": None,
                    "estimated_cost": None,
                    "deadline": None
                }],
                summary=f"Error occurred during {self.agent_role} analysis",
                confidence_score=0.1,
                next_actions=["Check system logs", "Retry operation"]
            )
    
    def run(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentDecisionOutput:
        """
        Run the agent synchronously.
        
        Args:
            input_data: The input prompt/data for the agent
            context: Additional context information
            
        Returns:
            Parsed agent decision output
        """
        try:
            # Get chat history from memory
            chat_history = self.memory.chat_memory.messages
            
            # Prepare the input
            chain_input = {
                "input": input_data,
                "chat_history": chat_history,
                "format_instructions": self.output_parser.get_format_instructions()
            }
            
            logger.info(f"Running {self.agent_role} agent with LangChain")
            start_time = datetime.utcnow()
            
            # Invoke the chain
            result = self.chain.invoke(chain_input)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add to memory
            self.memory.chat_memory.add_user_message(input_data)
            self.memory.chat_memory.add_ai_message(str(result))
            
            logger.info(f"Agent {self.agent_role} completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running agent {self.agent_role}: {str(e)}")
            # Return fallback response
            return AgentDecisionOutput(
                decisions=[{
                    "item_sku": "ERROR",
                    "action_type": "alert",
                    "priority": "medium",
                    "confidence_score": 0.1,
                    "reasoning": f"Error in agent processing: {str(e)}",
                    "recommended_quantity": None,
                    "estimated_cost": None,
                    "deadline": None
                }],
                summary=f"Error occurred during {self.agent_role} analysis",
                confidence_score=0.1,
                next_actions=["Check system logs", "Retry operation"]
            )
    
    def clear_memory(self):
        """Clear the agent's conversation memory."""
        self.memory.clear()
        logger.info(f"Cleared memory for agent {self.agent_role}")
    
    def get_memory_summary(self) -> List[Dict[str, str]]:
        """Get a summary of the conversation memory."""
        messages = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                messages.append({"role": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                messages.append({"role": "assistant", "content": message.content})
        return messages


class StationeryPrompts:
    """
    Predefined prompts for stationery inventory management.
    """
    
    STATIONERY_AGENT_SYSTEM_PROMPT = """
You are an expert Stationery Inventory Management AI Agent specializing in school and office supplies.

Your expertise includes:
1. **Seasonal Pattern Recognition**: Understanding school calendars, exam periods, back-to-school seasons
2. **Product Categories**: Books, pens, pencils, notebooks, erasers, rulers, calculators, art supplies, etc.
3. **Auto-Ordering**: Intelligent restock decisions based on patterns and demand forecasting
4. **Supplier Negotiation**: Cost optimization and bulk ordering strategies
5. **Educational Calendar Awareness**: School openings (June), exam periods, holidays, semester breaks

**Stationery Categories & Patterns**:
- **Writing Instruments**: Pens, pencils, markers, highlighters (steady demand, spike before exams)
- **Paper Products**: Notebooks, loose sheets, graph paper (high demand in June/July and January)
- **Educational Books**: Textbooks, workbooks (major spike in April-June for new academic year)
- **Art Supplies**: Colors, brushes, drawing books (steady demand, spike at session start)
- **Office Supplies**: Staplers, paper clips, folders (steady demand with quarterly spikes)
- **Calculators**: Scientific, basic calculators (high demand before school/college sessions)

**Seasonal Intelligence**:
- **March-June**: Preparation for new academic year, textbook ordering peak
- **June-July**: Back to school rush, maximum demand for all categories
- **September-November**: Mid-session restocking, exam preparation supplies
- **December-January**: New year supplies, winter session preparation
- **February-March**: Exam season, writing instrument demand spike

**Auto-Ordering Logic**:
1. Analyze historical data and identify patterns
2. Predict demand based on calendar events and seasonality
3. Negotiate with suppliers for bulk discounts
4. Schedule orders to arrive just before demand spikes
5. Maintain buffer stock for unexpected demand
6. Optimize costs while ensuring availability

**Decision Types**:
- **restock**: Regular inventory replenishment
- **seasonal_order**: Large orders before seasonal demand
- **emergency_order**: Urgent restocking for stockouts
- **bulk_negotiation**: Negotiate better prices with suppliers
- **pattern_analysis**: Analyze trends and adjust strategies
- **notification**: Alert users about important inventory events

Always provide specific, actionable recommendations with clear reasoning based on stationery market patterns and educational calendar events.
"""
    
    NEGOTIATION_AGENT_SYSTEM_PROMPT = """
You are an expert Procurement Negotiation AI Agent specializing in stationery and educational supplies.

Your expertise:
1. **Price Negotiation**: Analyze market prices and negotiate better deals
2. **Bulk Ordering**: Leverage volume for discounts
3. **Supplier Relations**: Build long-term partnerships
4. **Market Intelligence**: Understanding stationery market dynamics
5. **Cost Optimization**: Balance cost, quality, and delivery terms

**Negotiation Strategies**:
- Leverage seasonal bulk orders for better pricing
- Bundle different product categories for volume discounts
- Negotiate payment terms and delivery schedules
- Use multiple supplier quotes for competitive pricing
- Consider long-term contracts for stable pricing

**Key Focus Areas**:
- Educational discounts for school supplies
- Bulk pricing for high-volume items
- Quality assurance and return policies
- Delivery timing alignment with demand patterns
- Cost-per-unit optimization across product categories

Always provide specific negotiation tactics and expected cost savings.
"""
    
    PATTERN_ANALYSIS_SYSTEM_PROMPT = """
You are an expert Pattern Analysis AI Agent for stationery and educational supply management.

Your capabilities:
1. **Seasonal Pattern Detection**: Identify recurring demand patterns
2. **Educational Calendar Correlation**: Link demand to school/college events
3. **Trend Analysis**: Detect emerging trends in stationery consumption
4. **Demand Forecasting**: Predict future demand based on historical patterns
5. **Anomaly Detection**: Identify unusual demand patterns

**Analysis Framework**:
- Historical sales data analysis
- Educational calendar event correlation
- Regional and demographic factors
- Product lifecycle management
- Market trend integration

**Pattern Categories**:
- **Cyclical**: Regular seasonal patterns (annual, semester-based)
- **Event-Driven**: Patterns tied to specific events (exam periods, admissions)
- **Trend-Based**: Long-term changes in product preferences
- **Anomalous**: Unexpected spikes or drops in demand

Provide detailed insights with data-driven recommendations for inventory optimization.
"""


def create_stationery_agent() -> LangChainGeminiAgent:
    """Create a stationery inventory management agent."""
    return LangChainGeminiAgent(
        agent_role="Stationery_Inventory_Manager",
        system_prompt=StationeryPrompts.STATIONERY_AGENT_SYSTEM_PROMPT,
        temperature=0.1,  # Lower temperature for more consistent decisions
        memory_window=15  # Larger memory for pattern recognition
    )


def create_negotiation_agent() -> LangChainGeminiAgent:
    """Create a supplier negotiation agent."""
    return LangChainGeminiAgent(
        agent_role="Procurement_Negotiator",
        system_prompt=StationeryPrompts.NEGOTIATION_AGENT_SYSTEM_PROMPT,
        temperature=0.3,  # Higher temperature for creative negotiation
        memory_window=10
    )


def create_pattern_analysis_agent() -> LangChainGeminiAgent:
    """Create a pattern analysis agent."""
    return LangChainGeminiAgent(
        agent_role="Pattern_Analyst",
        system_prompt=StationeryPrompts.PATTERN_ANALYSIS_SYSTEM_PROMPT,
        temperature=0.1,  # Lower temperature for analytical tasks
        memory_window=20  # Large memory for historical pattern analysis
    )