from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RssFeedBase(BaseModel):
    name: str
    url: str
    category: str
    is_active: Optional[bool] = True

class RssFeedCreate(RssFeedBase):
    pass

class RssFeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class RssFeedResponse(RssFeedBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    
    class Config:
        orm_mode = True

class RssItemBase(BaseModel):
    title: str
    link: str
    description: str
    published_date: datetime

class RssItemCreate(RssItemBase):
    feed_id: int

class RssItemResponse(RssItemBase):
    id: int
    created_at: datetime
    feed_id: int
    
    class Config:
        orm_mode = True
