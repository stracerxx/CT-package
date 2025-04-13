# CT-5 Crypto Trading Bot - Setup Guide

## Overview

CT-5 is a full-stack crypto trading bot application with a retro 80s design. It features a FastAPI backend, AI trading logic engine, persistent chat module with multiple AI provider integrations, and a pixel art UI inspired by Nintendo.

## Prerequisites

- Docker and Docker Compose
- Git (optional, for cloning the repository)
- Internet connection
- API keys for AI providers (optional, but recommended for chat functionality)
- Exchange API keys (optional, for live trading)

## Quick Start

1. Clone or download the CT-5 repository
2. Navigate to the project directory
3. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Default admin login: username=`admin`, password=`admin`

> **IMPORTANT**: For security, please change the admin password and update API keys in the admin panel after initial setup.

## Manual Setup

If you prefer to set up the application manually, follow these steps:

1. Create a `.env` file in the `backend` directory (copy from `.env.example`)
2. Build and start the Docker containers:

```bash
docker-compose up -d --build
```

3. Initialize the database:

```bash
docker-compose exec backend python -c "
from config.database import engine, Base
from models.models import User, ApiKey, SystemPrompt, RssFeed, RssItem, TradingStrategy
Base.metadata.create_all(bind=engine)
"
```

4. Create an admin user:

```bash
docker-compose exec backend python -c "
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.models import User
from auth.auth_utils import get_password_hash

db = SessionLocal()
admin_user = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin'),
    is_active=True,
    is_admin=True
)
db.add(admin_user)
db.commit()
db.close()
"
```

## Configuration

### Environment Variables

The following environment variables can be configured in the `.env` file:

#### Database Configuration
- `DB_HOST`: Database host (default: postgres)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: ct5_db)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password

#### Authentication
- `JWT_SECRET`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 30)

#### AI Providers
- `OPENAI_API_KEY`: OpenAI API key
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `GEMINI_API_KEY`: Google Gemini API key
- `OPENROUTER_API_KEY`: OpenRouter API key
- `DEEPSEEK_API_KEY`: DeepSeek API key

#### Trading Configuration
- `DEFAULT_EXCHANGE`: Default cryptocurrency exchange (default: binance)
- `TRADING_MODE`: Trading mode, 'live' or 'paper' (default: paper)
- `MAX_TRADE_AMOUNT`: Maximum amount per trade in USDT
- `RISK_LEVEL`: Risk level, 'low', 'medium', or 'high' (default: medium)
- `MIN_MARKET_CONDITION_SCORE`: Minimum market condition score to allow trading
- `MARKET_CHECK_INTERVAL`: Interval in seconds to check market conditions
- `AUTO_RESUME_THRESHOLD`: Score threshold to auto-resume trading

#### RSS Feed Configuration
- `RSS_UPDATE_INTERVAL`: Interval in seconds to update RSS feeds
- `MAX_RSS_ITEMS`: Maximum number of RSS items to store per feed

#### API Configuration
- `API_HOST`: Host to bind the API server (default: 0.0.0.0)
- `API_PORT`: Port for the API server (default: 8000)
- `FRONTEND_URL`: URL of the frontend for CORS configuration

## Testing

CT-5 includes comprehensive test scripts to verify functionality and security:

### Integration Test

```bash
chmod +x integration_test.sh
./integration_test.sh
```

### Security Test

```bash
chmod +x security_test.sh
./security_test.sh
```

### Functional Test

```bash
chmod +x functional_test.sh
./functional_test.sh
```

## Production Deployment

For production deployment, follow these additional steps:

1. Update the `.env` file with production-appropriate values:
   - Set strong passwords for database and JWT secret
   - Configure proper API keys for AI providers
   - Set `TRADING_MODE` to 'paper' initially, then 'live' when ready

2. Configure proper SSL/TLS for secure connections:
   - Use a reverse proxy like Nginx or Traefik
   - Set up SSL certificates (Let's Encrypt recommended)

3. Update the `docker-compose.yml` file:
   - Remove port exposures for the database
   - Add volume mounts for persistent data
   - Configure restart policies

4. Set up monitoring and logging:
   - Configure log rotation
   - Set up monitoring tools like Prometheus/Grafana

## Troubleshooting

### Common Issues

1. **Docker containers not starting**
   - Check Docker logs: `docker-compose logs`
   - Verify port availability: `netstat -tuln`

2. **Database connection issues**
   - Verify database container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs postgres`

3. **API key errors**
   - Verify API keys are correctly set in the `.env` file
   - Check API provider status and quotas

4. **Frontend not connecting to backend**
   - Verify CORS settings in the backend
   - Check network connectivity between containers

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the logs: `docker-compose logs`
2. Run the test scripts to identify specific issues
3. Refer to the API documentation for endpoint details

## Maintenance

### Updating the Application

To update CT-5 to a newer version:

1. Pull the latest code
2. Run the setup script again
3. Check for any migration scripts if database schema has changed

### Backup and Restore

To backup the database:

```bash
docker-compose exec postgres pg_dump -U postgres ct5_db > backup.sql
```

To restore from backup:

```bash
cat backup.sql | docker-compose exec -T postgres psql -U postgres ct5_db
```
