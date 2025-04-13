from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ApiKeyBase(BaseModel):
    service: str
    api_key: str
    is_active: Optional[bool] = True

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyUpdate(BaseModel):
    service: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None

class ApiKeyResponse(ApiKeyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    
    class Config:
        orm_mode = True
