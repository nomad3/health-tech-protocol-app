from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatSessionCreate(BaseModel):
    protocol_id: int

class ChatSessionResponse(BaseModel):
    session_id: int
    protocol_id: int
    status: str
    created_at: datetime
    history: List[ChatMessage]

class ChatMessageRequest(BaseModel):
    session_id: int
    message: str

class ChatMessageResponse(BaseModel):
    response: str
    session_id: int
    status: str  # "in_progress" or "completed"
    eligibility_result: Optional[Dict[str, Any]] = None  # Only present if completed
