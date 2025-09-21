# VeriChain API Testing Guide

## 🚀 Quick Testing Commands

### Using PowerShell (Windows)

#### 1. Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

#### 2. Trigger AI Analysis

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/agent/analyze" -Method POST
```

#### 3. Get Inventory Summary

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/inventory/summary" -Method GET
```

#### 4. Get AI Insights

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/agent/insights" -Method GET
```

#### 5. View Dashboard Data

```powershell
# Supply Chain Manager Dashboard
Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/scm" -Method GET

# Finance Officer Dashboard
Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/finance" -Method GET
```

#### 6. Update Stock Level

```powershell
$stockUpdate = @{
    quantity = 150
    reason = "PowerShell test update"
    updated_by = "tester"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/inventory/items/1/stock/update" -Method POST -Body $stockUpdate -ContentType "application/json"
```

#### 7. Create New Sale Record

```powershell
$saleData = @{
    item_id = 1
    quantity_sold = 10
    unit_price = 1.20
    total_amount = 12.00
    customer_type = "INTERNAL"
    department = "Testing"
    sale_date = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/sales/record" -Method POST -Body $saleData -ContentType "application/json"
```

### Using cURL

#### 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

#### 2. Trigger AI Analysis

```bash
curl -X POST "http://localhost:8000/api/agent/analyze"
```

#### 3. Get All Inventory Items

```bash
curl -X GET "http://localhost:8000/api/inventory/items?limit=20"
```

#### 4. Get Recent Agent Decisions

```bash
curl -X GET "http://localhost:8000/api/agent/decisions/recent?limit=5"
```

#### 5. System Monitoring

```bash
curl -X GET "http://localhost:8000/api/monitoring/system/health"
curl -X GET "http://localhost:8000/api/monitoring/alerts/active"
```

## 🧪 Python Test Scripts

### Run Complete API Test Suite

```bash
cd server
python scripts/test_api_complete.py
```

### Create Sample Data

```bash
cd server
python scripts/create_sample_data.py
```

### Test Individual Agent

```bash
cd server
python scripts/test_agent.py
```

## 📊 Sample Request Bodies

### Add New Inventory Item

```json
{
  "name": "Premium Ballpoint Pen",
  "description": "High-quality ballpoint pen with smooth ink flow",
  "category": "WRITING_INSTRUMENTS",
  "current_stock": 100,
  "reorder_level": 20,
  "max_stock": 500,
  "unit_price": 2.5,
  "unit": "piece",
  "vendor_id": 1
}
```

### Create Purchase Order

```json
{
  "vendor_id": 1,
  "order_items": [
    {
      "item_id": 1,
      "quantity": 100,
      "unit_price": 1.15
    },
    {
      "item_id": 2,
      "quantity": 50,
      "unit_price": 0.85
    }
  ],
  "priority": "NORMAL",
  "notes": "Quarterly stationery restock"
}
```

### Record Sales Transaction

```json
{
  "item_id": 1,
  "quantity_sold": 5,
  "unit_price": 1.2,
  "total_amount": 6.0,
  "customer_type": "INTERNAL",
  "department": "HR",
  "sale_date": "2024-01-15T10:30:00"
}
```

### Add New Vendor

```json
{
  "name": "Premium Office Supplies Ltd",
  "contact_person": "John Smith",
  "email": "john@premiumoffice.com",
  "phone": "+1-555-0123",
  "address": "123 Business Ave, Suite 456, City, State 12345",
  "rating": 4.5,
  "is_active": true
}
```

## 🎯 Expected Response Examples

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "0.1.0",
  "database": "connected",
  "ai_agent": "ready"
}
```

### Agent Analysis Response

```json
{
  "status": "completed",
  "message": "Analysis completed successfully",
  "insights_generated": 5,
  "decisions_made": 3,
  "actions_taken": 2,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Inventory Summary Response

```json
{
  "total_items": 25,
  "total_value": 15420.5,
  "low_stock_count": 3,
  "categories": {
    "WRITING_INSTRUMENTS": 8,
    "PAPER_PRODUCTS": 6,
    "OFFICE_SUPPLIES": 5,
    "FILING_SUPPLIES": 4,
    "DESK_ACCESSORIES": 2
  },
  "alerts": [
    {
      "item_id": 1,
      "name": "Blue Ballpoint Pen",
      "current_stock": 15,
      "reorder_level": 20,
      "status": "reorder_needed"
    }
  ]
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Server Not Running**

   ```bash
   # Start the server
   cd server
   python app/main.py
   ```

2. **Database Not Initialized**

   ```bash
   # Initialize database
   python scripts/init_db.py
   ```

3. **Missing Environment Variables**

   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```

4. **Port Already in Use**
   ```bash
   # Check what's running on port 8000
   netstat -ano | findstr :8000
   ```

### Validation Steps

1. **Check Server Status**

   ```bash
   curl -X GET "http://localhost:8000/health"
   ```

2. **Verify Database Connection**

   ```bash
   curl -X GET "http://localhost:8000/api/monitoring/system/health"
   ```

3. **Test AI Agent**
   ```bash
   curl -X POST "http://localhost:8000/api/agent/analyze"
   ```

## 📈 Performance Testing

### Load Testing with Multiple Requests

```powershell
# PowerShell parallel requests
1..10 | ForEach-Object -Parallel {
    Invoke-RestMethod -Uri "http://localhost:8000/api/inventory/summary" -Method GET
}
```

### Batch Operations

```bash
# Multiple agent analyses
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/agent/analyze"
  sleep 2
done
```

## 🛠️ Development Testing

### API Documentation

- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Database Inspection

```bash
# View database directly (if using SQLite)
sqlite3 verichain.db ".tables"
sqlite3 verichain.db "SELECT * FROM stationery_items LIMIT 5;"
```
