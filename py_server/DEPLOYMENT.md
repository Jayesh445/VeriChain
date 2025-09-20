# Production Deployment Guide

## 🚀 VeriChain Production Deployment

This guide covers deploying the VeriChain Stationery Inventory Management System to production.

### Prerequisites

- **Python 3.11+**
- **UV Package Manager** (https://docs.astral.sh/uv/)
- **Google Gemini API Key**
- **Production Database** (PostgreSQL recommended)
- **Reverse Proxy** (Nginx recommended)

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd py_server

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv install
```

### 2. Environment Configuration

Create a production `.env` file:

```bash
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Required: Google Gemini API Key
GEMINI_API_KEY=your_production_gemini_api_key

# Production Database (PostgreSQL recommended)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/verichain

# CORS Configuration for your frontend domain
ALLOWED_ORIGINS=https://your-frontend-domain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Security Settings
SECRET_KEY=your_super_secret_key_here

# Performance Settings
MAX_WORKERS=4
WORKER_TIMEOUT=300
```

### 3. Database Setup

#### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE verichain;
CREATE USER verichain_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE verichain TO verichain_user;
\q
```

#### Database Initialization

```bash
# Run database migrations (when available)
uv run python -c "
import asyncio
from app.services.database import init_database
asyncio.run(init_database())
"
```

### 4. System Service Setup

Create systemd service file `/etc/systemd/system/verichain.service`:

```ini
[Unit]
Description=VeriChain Stationery Inventory Management API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/py_server
Environment=PATH=/path/to/your/py_server/.venv/bin
EnvironmentFile=/path/to/your/py_server/.env
ExecStart=/path/to/your/py_server/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable verichain
sudo systemctl start verichain
sudo systemctl status verichain
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/verichain`:

```nginx
server {
    listen 80;
    server_name your-api-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-api-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/ssl/cert.pem;
    ssl_certificate_key /path/to/your/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_dhparam /path/to/dhparam.pem;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint (bypass proxy for faster response)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/verichain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-api-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Monitoring and Logging

#### Log Configuration

Update your `.env` for structured logging:

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/verichain/app.log
```

#### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop

# Monitor the service
sudo journalctl -u verichain -f

# Monitor system resources
htop

# Monitor database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='verichain';"
```

### 8. Backup Strategy

#### Database Backup

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/verichain"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/verichain_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -U verichain_user -h localhost verichain > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### Application Backup

```bash
#!/bin/bash
# backup_application.sh

BACKUP_DIR="/backups/verichain"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/path/to/your/py_server"

tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude=".git" \
    "$APP_DIR"

echo "Application backup completed"
```

#### Automated Backups

```bash
# Add to crontab
sudo crontab -e

# Daily database backup at 2 AM
0 2 * * * /path/to/backup_database.sh

# Weekly application backup on Sunday at 3 AM
0 3 * * 0 /path/to/backup_application.sh
```

### 9. Performance Optimization

#### Database Optimization

```sql
-- PostgreSQL optimizations
-- Add indexes for frequently queried columns
CREATE INDEX idx_inventory_items_category ON inventory_items(category);
CREATE INDEX idx_sales_data_item_date ON sales_data(item_id, sale_date);
CREATE INDEX idx_agent_decisions_created ON agent_decisions(created_at);

-- Analyze tables for query planning
ANALYZE inventory_items;
ANALYZE sales_data;
ANALYZE agent_decisions;
```

#### Application Optimization

```bash
# In production .env
WORKERS=4  # Adjust based on CPU cores
WORKER_CLASS=uvicorn.workers.UvicornWorker
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
TIMEOUT=300
KEEPALIVE=2
```

### 10. Security Checklist

- [ ] **Environment Variables**: All secrets in environment variables, not code
- [ ] **SSL/TLS**: HTTPS enabled with strong cipher suites
- [ ] **Firewall**: Only necessary ports open (80, 443, 22)
- [ ] **Database**: Database user with minimal required permissions
- [ ] **Updates**: Regular system and dependency updates
- [ ] **Backups**: Automated, tested backup and restore procedures
- [ ] **Monitoring**: Error tracking and performance monitoring
- [ ] **Rate Limiting**: API rate limiting configured
- [ ] **CORS**: Proper CORS configuration for frontend domains

### 11. Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying VeriChain to Production..."

# Pull latest code
git pull origin main

# Install/update dependencies
uv install

# Run tests
uv run pytest tests/

# Database migrations (if any)
uv run python -c "
import asyncio
from app.services.database import init_database
asyncio.run(init_database())
"

# Restart service
sudo systemctl restart verichain

# Check service status
sleep 5
sudo systemctl status verichain

# Test health endpoint
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    sudo systemctl status verichain
    sudo journalctl -u verichain -n 50
    exit 1
}

echo "✅ Deployment completed successfully"
```

### 12. Rollback Procedure

Create `rollback.sh`:

```bash
#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <commit-hash>"
    exit 1
fi

COMMIT_HASH=$1

echo "🔄 Rolling back to commit: $COMMIT_HASH"

# Backup current state
git stash

# Checkout target commit
git checkout $COMMIT_HASH

# Reinstall dependencies
uv install

# Restart service
sudo systemctl restart verichain

# Verify
sleep 5
curl -f http://localhost:8000/health

echo "✅ Rollback completed"
```

### 13. Health Checks and Monitoring

#### Application Health Check

```bash
#!/bin/bash
# health_check.sh

API_URL="http://localhost:8000"
HEALTH_ENDPOINT="$API_URL/health"

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)

if [ $response -eq 200 ]; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API health check failed (HTTP $response)"

    # Check service status
    systemctl is-active verichain

    # Show recent logs
    journalctl -u verichain -n 20 --no-pager

    exit 1
fi
```

### 14. Troubleshooting

#### Common Issues and Solutions

**Service won't start:**

```bash
# Check logs
sudo journalctl -u verichain -n 50

# Check configuration
uv run python -c "from app.core.config import settings; print(settings.validate_required_settings())"

# Test manually
cd /path/to/py_server
uv run python main.py
```

**Database connection issues:**

```bash
# Test database connection
psql -U verichain_user -h localhost -d verichain -c "SELECT 1;"

# Check database service
sudo systemctl status postgresql
```

**High memory usage:**

```bash
# Monitor memory usage
htop

# Adjust worker count in systemd service
sudo systemctl edit verichain
```

**SSL certificate issues:**

```bash
# Check certificate expiry
sudo certbot certificates

# Renew certificates
sudo certbot renew
```

This completes the production deployment guide for the VeriChain system.
