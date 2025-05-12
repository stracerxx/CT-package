"""
Database initialization script for CT-5 Platform
Run this script to create database tables and initial data
"""

import logging
from sqlalchemy.orm import Session
from config.database import engine, Base, SessionLocal
from models.models import User, ApiKey, SystemPrompt, RssFeed, RssItem, TradingStrategy
from auth.auth_utils import get_password_hash
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create admin user if it doesn't exist
        db = SessionLocal()
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            logger.info("Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                hashed_password=get_password_hash('admin'),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")
        
        # Add sample RSS feeds
        if db.query(RssFeed).count() == 0:
            logger.info("Adding sample RSS feeds...")
            sample_feeds = [
                {'name': 'CoinDesk', 'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'category': 'news'},
                {'name': 'Cointelegraph', 'url': 'https://cointelegraph.com/rss', 'category': 'news'},
                {'name': 'Bitcoin Magazine', 'url': 'https://bitcoinmagazine.com/feed', 'category': 'bitcoin'}
            ]
            
            admin_id = db.query(User).filter(User.username == 'admin').first().id
            
            for feed_data in sample_feeds:
                new_feed = RssFeed(
                    name=feed_data['name'],
                    url=feed_data['url'],
                    category=feed_data['category'],
                    is_active=True,
                    user_id=admin_id
                )
                db.add(new_feed)
                logger.info(f"Added RSS feed: {feed_data['name']}")
            
            db.commit()
            logger.info("Sample RSS feeds added successfully")
        
        db.close()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")
