#!/bin/bash

# CT-5 Crypto Trading Bot Setup Script
echo "====================================="
echo "  CT-5 Crypto Trading Bot Setup"
echo "====================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker and Docker Compose are required but not installed."
    echo "Please install Docker and Docker Compose first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f ./backend/.env ]; then
    echo "Creating .env file from example..."
    cp ./backend/.env.example ./backend/.env
    echo "Please edit ./backend/.env to set your API keys and other configuration."
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Initialize the database
echo "Initializing database..."
docker-compose exec backend python -c "
from config.database import engine, Base
from models.models import User, ApiKey, SystemPrompt, RssFeed, RssItem, TradingStrategy
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Create admin user if it doesn't exist
echo "Creating admin user..."
docker-compose exec backend python -c "
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.models import User
from auth.auth_utils import get_password_hash
import os

db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin_user = User(
        username='admin',
        email='admin@example.com',
        hashed_password=get_password_hash('admin'),
        is_active=True,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    print('Admin user created successfully')
else:
    print('Admin user already exists')
db.close()
"

# Load default system prompt
echo "Loading default system prompt..."
docker-compose exec backend python -c "
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.models import SystemPrompt, User
import os

db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    default_prompt = db.query(SystemPrompt).filter(SystemPrompt.name == 'Default CT-5 Persona').first()
    if not default_prompt:
        with open('/app/ct5_system_persona.md', 'r') as f:
            prompt_content = f.read()
        
        default_prompt = SystemPrompt(
            name='Default CT-5 Persona',
            content=prompt_content,
            is_active=True,
            user_id=admin.id
        )
        db.add(default_prompt)
        db.commit()
        print('Default system prompt loaded successfully')
    else:
        print('Default system prompt already exists')
db.close()
"

# Add sample RSS feeds
echo "Adding sample RSS feeds..."
docker-compose exec backend python -c "
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.models import RssFeed, User
import os

db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    sample_feeds = [
        {'name': 'CoinDesk', 'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'category': 'news'},
        {'name': 'Cointelegraph', 'url': 'https://cointelegraph.com/rss', 'category': 'news'},
        {'name': 'Bitcoin Magazine', 'url': 'https://bitcoinmagazine.com/feed', 'category': 'bitcoin'}
    ]
    
    for feed_data in sample_feeds:
        existing_feed = db.query(RssFeed).filter(RssFeed.url == feed_data['url']).first()
        if not existing_feed:
            new_feed = RssFeed(
                name=feed_data['name'],
                url=feed_data['url'],
                category=feed_data['category'],
                is_active=True,
                user_id=admin.id
            )
            db.add(new_feed)
            print(f'Added RSS feed: {feed_data['name']}')
    
    db.commit()
db.close()
"

echo "====================================="
echo "  CT-5 Setup Complete!"
echo "====================================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Admin login: username=admin, password=admin"
echo ""
echo "IMPORTANT: For security, please change the admin password and update API keys in the admin panel."
echo "====================================="
