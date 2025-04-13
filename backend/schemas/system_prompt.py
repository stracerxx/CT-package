from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SystemPromptBase(BaseModel):
    name: str
    content: str
    is_active: Optional[bool] = True

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class SystemPromptResponse(SystemPromptBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    
    class Config:
        orm_mode = True
