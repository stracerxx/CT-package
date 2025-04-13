from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    role: str
    provider: str
    timestamp: float

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    count: int

class ProviderResponse(BaseModel):
    provider: str
    timestamp: float
