"""Validated API request and response shapes."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    assistant_id: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: str | None = Field(default=None, max_length=36)


class ChatResponse(BaseModel):
    conversation_id: str
    assistant_id: str
    title: str
    message: str
    created_at: datetime


class AssistantResponse(BaseModel):
    id: str
    name: str
    description: str
    capabilities: list[str]
    available: bool
    icon: str


class ConversationSummary(BaseModel):
    id: str
    assistant_id: str
    assistant_name: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(BaseModel):
    id: str
    assistant_id: str
    assistant_name: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
