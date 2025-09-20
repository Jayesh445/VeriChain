# VeriChain Stationery Inventory Management System

🤖 **AI-Powered Inventory Management with Auto-Ordering and Pattern Recognition**

A comprehensive agentic AI framework for intelligent stationery inventory management, featuring seasonal demand prediction, educational calendar awareness, automated supplier negotiation, and real-time decision making.

## 🎯 Key Features

### 🤖 AI-Powered Intelligence
- **LangChain + Google Gemini Integration**: Advanced AI agents for inventory decision making
- **Seasonal Pattern Recognition**: Automatically detects school seasons, exam periods, and demand cycles
- **Educational Calendar Awareness**: Predicts demand based on academic calendar events
- **Smart Auto-Ordering**: Intelligent order placement with supplier negotiation
- **Predictive Analytics**: Low-stock prediction and demand forecasting

### 📊 Comprehensive Management
- **Real-time Inventory Tracking**: Live stock levels and valuation
- **Category-Specific Logic**: Specialized handling for books, pens, notebooks, art supplies
- **Multi-Priority Alerts**: Critical, high, medium, and low priority notifications
- **Supplier Management**: Automated negotiation and order management
- **Analytics Dashboard**: Comprehensive insights and performance metrics

### ⚡ Technical Excellence
- **Async FastAPI**: High-performance REST API with async/await
- **Database Persistence**: SQLAlchemy with async support
- **Robust Error Handling**: Retry logic and comprehensive logging
- **Real-time Notifications**: Instant alerts and status updates
- **Production-Ready**: Full production deployment configuration

## 🏗️ Architecture

```
py_server/
├── app/
│   ├── agents/                 # AI Agents
│   │   └── stationery_agent.py # Core inventory agent
│   ├── api/                    # FastAPI endpoints
│   │   ├── agents.py          # Agent operations API
│   │   └── dashboard.py       # Dashboard API
│   ├── core/                  # Core configuration
│   │   └── config.py          # Settings and config
│   ├── models/                # Data models
│   │   └── __init__.py        # Pydantic models
│   ├── services/              # Business services
│   │   ├── database.py        # Database operations
│   │   ├── gemini_client.py   # Gemini API client
│   │   └── notifications.py   # Notification system
│   ├── utils/                 # Utilities
│   │   └── logging.py         # Logging configuration
│   └── main.py               # FastAPI application
├── tests/                     # Test suite
│   └── test_stationery_system.py
├── scripts/                   # Deployment scripts
│   └── start_server.py       # Production startup
├── main.py                   # Application entry point
├── pyproject.toml           # UV package configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- Google Gemini API key

### Installation

1. **Clone and setup:**
```bash
cd py_server
uv install
```

2. **Environment configuration:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./inventory.db
DEBUG=true
```

3. **Start development server:**
```bash
python main.py
```

4. **Or use the production script:**
```bash
python scripts/start_server.py
```

## 📡 API Endpoints

### Core Endpoints
- **`GET /`** - System information and welcome
- **`GET /health`** - Health check with component status
- **`GET /docs`** - Interactive API documentation
- **`GET /redoc`** - Alternative API documentation

### Agent Operations
- **`POST /api/v1/agents/analyze`** - Analyze inventory and get AI recommendations
- **`GET /api/v1/agents/decisions`** - Get recent agent decisions
- **`POST /api/v1/agents/execute-decision/{decision_id}`** - Execute agent decision

### Dashboard & Analytics
- **`GET /api/v1/dashboard/summary`** - Dashboard overview
- **`GET /api/v1/dashboard/inventory`** - Inventory analytics
- **`GET /api/v1/dashboard/categories`** - Category-wise statistics
- **`GET /api/v1/dashboard/alerts`** - Active alerts and notifications

### System Monitoring
- **`GET /api/v1/system/stats`** - Comprehensive system statistics

## 🤖 AI Agent Capabilities

### Stationery Inventory Agent
The core AI agent provides intelligent inventory management with:

```python
# Key capabilities
- Seasonal demand analysis (back-to-school, exam periods)
- Educational calendar integration
- Category-specific stock management
- Automated order decision making
- Supplier negotiation logic
- Risk assessment and confidence scoring
```

### Decision Types
- **AUTO_ORDER**: Automatic order placement
- **RESTOCK_ALERT**: Low stock notifications  
- **PRICE_NEGOTIATION**: Supplier price negotiations
- **SEASONAL_PREP**: Seasonal demand preparation
- **EMERGENCY_ORDER**: Critical stock situations

### Example AI Analysis
```json
{
  "decision_type": "AUTO_ORDER",
  "confidence_score": 0.92,
  "reasoning": "Back-to-school season approaching in 2 weeks. Historical data shows 300% increase in notebook demand. Current stock: 50 units, recommended order: 500 units.",
  "category": "NOTEBOOKS",
  "seasonal_factor": "BACK_TO_SCHOOL",
  "urgency": "HIGH"
}
```

## 📊 Data Models

### Inventory Item
```python
class InventoryItem(BaseModel):
    id: str
    name: str
    category: StationeryCategory
    current_stock: int
    min_stock_level: int
    max_stock_level: int
    unit_price: float
    supplier: str
    last_order_date: Optional[datetime]
    seasonal_demand_pattern: Dict[str, float]
```

### Agent Decision
```python
class AgentDecision(BaseModel):
    id: str
    decision_type: DecisionType
    item_id: str
    reasoning: str
    confidence_score: float
    recommended_action: Dict[str, Any]
    priority: Priority
    created_at: datetime
    approved: bool = False
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional with defaults
DATABASE_URL=sqlite+aiosqlite:///./inventory.db
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Database Configuration
The system uses SQLAlchemy with async support. Default SQLite database for development, easily configurable for PostgreSQL/MySQL in production.

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=app

# Run specific test
uv run pytest tests/test_stationery_system.py::test_seasonal_analysis
```

## 📈 Monitoring & Logging

### Structured Logging
- Loguru-based structured logging
- Configurable log levels
- JSON formatting for production
- Correlation IDs for request tracking

### Health Monitoring
- Database connectivity checks
- AI agent status monitoring
- Notification system health
- Performance metrics tracking

## 🚀 Production Deployment

### Using the Production Script
```bash
python scripts/start_server.py
```

### Manual Production Setup
```bash
# Set environment
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=INFO

# Start with Gunicorn/Uvicorn
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment (Future)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv install
CMD ["python", "main.py"]
```

## 🔮 AI Features in Detail

### Seasonal Intelligence
- **Back-to-School Detection**: Automatically increases book and notebook orders
- **Exam Period Awareness**: Boosts pen, paper, and calculator inventory
- **Holiday Patterns**: Manages gift stationery and seasonal items
- **Weather-Based Adjustments**: Accounts for weather impact on demand

### Negotiation Intelligence
- **Price Comparison**: Compares supplier prices automatically
- **Bulk Discount Optimization**: Calculates optimal order quantities
- **Delivery Time Optimization**: Balances cost vs. delivery speed
- **Risk Assessment**: Evaluates supplier reliability and market conditions

### Pattern Recognition
- **Historical Analysis**: Learns from past sales patterns
- **Trend Detection**: Identifies emerging product trends
- **Anomaly Detection**: Flags unusual demand patterns
- **Predictive Modeling**: Forecasts future inventory needs

## 🛠️ Development

### Code Structure
- **Type Hints**: Comprehensive type annotations
- **Async/Await**: Full async support throughout
- **Error Handling**: Robust exception handling
- **Testing**: Comprehensive test coverage
- **Documentation**: Detailed docstrings and comments

### Contributing Guidelines
1. Follow existing code style and patterns
2. Add tests for new features
3. Update documentation for API changes
4. Use type hints for all functions
5. Follow async/await patterns

## 📚 Technology Stack

- **🐍 Python 3.11+**: Modern Python with async support
- **⚡ FastAPI**: High-performance async web framework
- **🤖 LangChain**: AI agent orchestration framework
- **🧠 Google Gemini**: Large language model for intelligence
- **💾 SQLAlchemy**: Async ORM for database operations
- **📦 UV**: Modern Python package management
- **📊 Pydantic**: Data validation and serialization
- **📝 Loguru**: Structured logging
- **🔄 Tenacity**: Retry logic for reliability

## 📄 License

This project is part of the VeriChain inventory management system.

## 🤝 Support

For technical support or questions about the AI inventory system:
1. Check the API documentation at `/docs`
2. Review the health check endpoint at `/health`
3. Examine logs for detailed error information
4. Test individual components using the test suite

---

**🎯 Built for intelligent stationery inventory management with AI-powered decision making and educational calendar awareness.**
