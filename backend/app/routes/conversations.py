from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import ConversationDetail, ConversationSummary, MessageResponse
from app.services import conversation_service

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummary])
def get_conversations(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    return conversation_service.list_conversations(limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str) -> dict:
    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(conversation_id: str) -> list[dict]:
    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation_service.list_messages(conversation_id)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_conversation(conversation_id: str) -> None:
    deleted = conversation_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
