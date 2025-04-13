from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import feedparser
from datetime import datetime
import time

from config.database import get_db
from models.models import RssFeed, RssItem, User
from schemas.rss_feeds import RssFeedCreate, RssFeedUpdate, RssFeedResponse, RssItemResponse
from auth.auth_utils import get_current_active_user, get_current_admin_user

router = APIRouter()

# Helper function to parse and update RSS feed items
def parse_and_update_feed(feed_id: int, db: Session):
    """Parse RSS feed and update items in database"""
    # Get the feed
    feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if not feed:
        return
    
    # Parse the feed
    parsed_feed = feedparser.parse(feed.url)
    
    # Get existing items to avoid duplicates
    existing_links = set(item.link for item in db.query(RssItem.link).filter(RssItem.feed_id == feed_id).all())
    
    # Add new items
    for entry in parsed_feed.entries[:50]:  # Limit to 50 items
        if entry.link not in existing_links:
            # Parse published date
            published_date = None
            if hasattr(entry, 'published_parsed'):
                published_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed'):
                published_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            else:
                published_date = datetime.now()
            
            # Create new item
            new_item = RssItem(
                title=entry.title,
                link=entry.link,
                description=entry.summary if hasattr(entry, 'summary') else "",
                published_date=published_date,
                feed_id=feed_id
            )
            db.add(new_item)
    
    db.commit()

@router.post("", response_model=RssFeedResponse, status_code=status.HTTP_201_CREATED)
async def create_rss_feed(
    rss_feed: RssFeedCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new RSS feed (admin only)
    """
    # Check if feed with this URL already exists
    existing_feed = db.query(RssFeed).filter(RssFeed.url == rss_feed.url).first()
    if existing_feed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RSS feed with URL '{rss_feed.url}' already exists"
        )
    
    # Create new RSS feed
    db_rss_feed = RssFeed(
        name=rss_feed.name,
        url=rss_feed.url,
        category=rss_feed.category,
        is_active=rss_feed.is_active,
        user_id=current_user.id
    )
    
    db.add(db_rss_feed)
    db.commit()
    db.refresh(db_rss_feed)
    
    # Parse and update feed items in background
    background_tasks.add_task(parse_and_update_feed, db_rss_feed.id, db)
    
    return db_rss_feed

@router.get("", response_model=List[RssFeedResponse])
async def read_rss_feeds(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all RSS feeds with optional category filter
    """
    query = db.query(RssFeed)
    if category:
        query = query.filter(RssFeed.category == category)
    
    rss_feeds = query.offset(skip).limit(limit).all()
    return rss_feeds

@router.get("/{feed_id}", response_model=RssFeedResponse)
async def read_rss_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get RSS feed by ID
    """
    rss_feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if rss_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS feed with ID {feed_id} not found"
        )
    return rss_feed

@router.put("/{feed_id}", response_model=RssFeedResponse)
async def update_rss_feed(
    feed_id: int,
    rss_feed_update: RssFeedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update RSS feed by ID (admin only)
    """
    rss_feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if rss_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS feed with ID {feed_id} not found"
        )
    
    # Update fields if provided
    if rss_feed_update.name is not None:
        rss_feed.name = rss_feed_update.name
    
    if rss_feed_update.url is not None and rss_feed_update.url != rss_feed.url:
        # Check if new URL already exists
        existing_feed = db.query(RssFeed).filter(RssFeed.url == rss_feed_update.url).first()
        if existing_feed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"RSS feed with URL '{rss_feed_update.url}' already exists"
            )
        rss_feed.url = rss_feed_update.url
    
    if rss_feed_update.category is not None:
        rss_feed.category = rss_feed_update.category
    
    if rss_feed_update.is_active is not None:
        rss_feed.is_active = rss_feed_update.is_active
    
    db.commit()
    db.refresh(rss_feed)
    
    return rss_feed

@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rss_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete RSS feed by ID (admin only)
    """
    rss_feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if rss_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS feed with ID {feed_id} not found"
        )
    
    # Delete associated items first
    db.query(RssItem).filter(RssItem.feed_id == feed_id).delete()
    
    # Delete the feed
    db.delete(rss_feed)
    db.commit()
    
    return None

@router.get("/{feed_id}/items", response_model=List[RssItemResponse])
async def read_rss_feed_items(
    feed_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get RSS feed items by feed ID
    """
    # Check if feed exists
    rss_feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if rss_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS feed with ID {feed_id} not found"
        )
    
    # Get items
    items = db.query(RssItem).filter(
        RssItem.feed_id == feed_id
    ).order_by(
        RssItem.published_date.desc()
    ).offset(skip).limit(limit).all()
    
    return items

@router.post("/{feed_id}/refresh", response_model=RssFeedResponse)
async def refresh_rss_feed(
    feed_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually refresh RSS feed items
    """
    # Check if feed exists
    rss_feed = db.query(RssFeed).filter(RssFeed.id == feed_id).first()
    if rss_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS feed with ID {feed_id} not found"
        )
    
    # Parse and update feed items in background
    background_tasks.add_task(parse_and_update_feed, feed_id, db)
    
    return rss_feed
