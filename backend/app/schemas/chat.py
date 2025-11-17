"""
Chat and conversation schemas.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    include_history: bool = True


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str
    conversation_id: str
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    """Conversation history."""
    conversation_id: str
    messages: List[ChatMessage]
    user_id: int
    created_at: datetime
    updated_at: datetime


class OnboardingResponse(BaseModel):
    """Response from onboarding conversation."""
    message: str
    onboarding_complete: bool
    user_profile: Optional[Dict[str, Any]] = None
    next_steps: Optional[List[str]] = None
