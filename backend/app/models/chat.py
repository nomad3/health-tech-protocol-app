from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class ChatSessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)

    status = Column(String, default=ChatSessionStatus.IN_PROGRESS)

    # Store the conversation history as a list of message objects
    # [{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]
    history = Column(JSON, default=list)

    # Store extracted data points (age, medical_history, etc.)
    collected_data = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="chat_sessions")
    protocol = relationship("Protocol", backref="chat_sessions")
