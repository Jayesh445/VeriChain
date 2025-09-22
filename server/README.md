# VeriChain Agentic Supply Chain Management

A complete autonomous AI-powered supply chain management system specifically designed for stationery inventory management.

## 🚀 Quick Start

1. **Install dependencies**:

   ```bash
   cd server
   python scripts/setup.py
   ```

2. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Start the server**:

   ```bash
   python scripts/start_server.py
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

Key environment variables:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./verichain.db

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
AGENT_MODEL=gemini-pro
AGENT_TEMPERATURE=0.1

# Business Rules
REORDER_THRESHOLD_PERCENTAGE=20.0
ANOMALY_DETECTION_THRESHOLD=2.0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## 🎯 AI Decision Types

1. **Reorder Recommendations**

   - Identifies items below reorder level
   - Calculates optimal order quantities
   - Considers sales velocity and lead times

2. **Anomaly Alerts**

   - Detects unusual sales patterns
   - Identifies inventory discrepancies
   - Flags system issues

3. **Vendor Risk Assessments**
   - Evaluates delivery performance
   - Identifies reliability issues
   - Suggests vendor diversification

## 🔬 Testing

Run tests:

```bash
python -m pytest tests/
```

Test the AI agent:

```bash
python scripts/test_agent.py
```

## 📈 Monitoring & Maintenance

### Health Checks

- Database connectivity
- AI agent activity
- Workflow status
- System performance

### Cleanup Operations

- Automatic workflow cleanup
- Decision history management
- Log rotation

## 🔒 Security Features

- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Error handling and logging
- Audit trail for all decisions

## 🚧 Development

### Project Structure

```
server/
├── app/
│   ├── agents/          # AI agents and orchestration
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Configuration and database
│   ├── models/          # Data models and schemas
│   └── services/        # Business logic services
├── scripts/             # Setup and utility scripts
├── tests/               # Test suite
└── pyproject.toml       # Dependencies and configuration
```

### Adding New Features

1. **New Analysis Types**: Extend `analysis_engine.py`
2. **New Decision Types**: Add to `AgentDecisionType` enum
3. **New API Endpoints**: Create new routers in `app/api/`
4. **New Data Models**: Add to `app/models/__init__.py`

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure proper error handling and logging

## 📄 License

This project is part of the VeriChain supply chain management system.

---

**Built with**: FastAPI, SQLAlchemy, Google Gemini AI, LangChain, Pydantic

### Autonomous Decision Making

- **Stock Analysis**: Automatically monitors inventory levels and identifies items needing reorder
- **Sales Trend Analysis**: Detects patterns and anomalies in sales data
- **Vendor Performance**: Tracks and evaluates vendor reliability and delivery performance
- **Demand Forecasting**: Predicts future demand based on historical sales data

### Intelligent Workflows

- **Data Fetch**: Retrieves current inventory, sales, and vendor data
- **Analysis**: Performs statistical analysis and anomaly detection
- **AI Reasoning**: Uses Google Gemini to generate intelligent recommendations
- **Decision Making**: Converts analysis into actionable decisions
- **Action Execution**: Automatically executes approved actions (reorders, alerts)
- **Logging**: Maintains audit trail of all decisions and actions

## 📊 API Endpoints

### Agent Operations

- `POST /api/agent/analyze` - Trigger complete AI analysis
- `GET /api/agent/insights` - Get latest AI insights and recommendations
- `GET /api/agent/decisions/recent` - View recent agent decisions
- `GET /api/agent/performance/summary` - Get agent performance metrics

### Inventory Management

- `GET /api/inventory/items` - List all inventory items
- `GET /api/inventory/summary` - Get inventory overview
- `GET /api/inventory/alerts` - Get current inventory alerts
- `POST /api/inventory/items/{item_id}/stock/update` - Update stock levels

### Dashboard & Reporting

- `GET /api/dashboard/scm` - Supply Chain Manager dashboard
- `GET /api/dashboard/finance` - Finance Officer dashboard
- `GET /api/dashboard/overview` - General overview dashboard

### Monitoring

- `GET /api/monitoring/system/health` - System health status
- `GET /api/monitoring/workflows/active` - Active workflow status
- `GET /api/monitoring/alerts/active` - Current system alerts

## 🏗️ Architecture

### Core Components

1. **AI Agent (`app/agents/`)**

   - `SupplyChainAgent`: Main AI reasoning engine using Google Gemini
   - `AgentWorkflowOrchestrator`: Coordinates multi-step workflows

2. **Analysis Engine (`app/services/analysis_engine.py`)**

   - `StockAnalyzer`: Stock level and reorder analysis
   - `SalesTrendAnalyzer`: Sales pattern analysis
   - `AnomalyDetector`: Statistical anomaly detection
   - `DemandForecaster`: Demand prediction
   - `VendorAnalyzer`: Vendor performance analysis

3. **Database Services (`app/services/database.py`)**

   - `InventoryService`: Inventory CRUD operations
   - `SalesService`: Sales data management
   - `VendorService`: Vendor management
   - `OrderService`: Order processing
   - `AgentDecisionService`: Decision logging and retrieval

4. **Data Models (`app/models/`)**
   - SQLAlchemy models for all entities
   - Pydantic schemas for API validation
   - Enums for standardized values

### Workflow Process

```
1. Data Fetch → 2. Analysis → 3. AI Reasoning → 4. Decision Making → 5. Action Execution → 6. Logging
```

## 🗄️ Database Schema

### Core Entities

- **StationeryItem**: Inventory items with stock levels, reorder points
- **Vendor**: Supplier information and performance metrics
- **VendorItem**: Vendor-specific pricing and terms
- **SalesRecord**: Transaction history
- **Order**: Purchase orders and fulfillment tracking
- **AgentDecision**: AI decision audit trail

### Categories

- Writing instruments (pens, pencils, markers)
- Paper products (copy paper, notebooks, sticky notes)
- Office supplies (clips, staplers, tape)
- Filing supplies (folders, binders, labels)
- Desk accessories (organizers, calculators)

## 🔧 Configuration

- `DATABASE_URL` - Database connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `REDIS_URL` - Redis connection string (optional)

## Architecture

The system follows an agentic architecture where AI agents autonomously:

1. Monitor inventory and sales data
2. Analyze trends and detect anomalies
3. Make reordering decisions
4. Generate role-specific insights
5. Coordinate vendor negotiations
6. Log all decisions with explanations
