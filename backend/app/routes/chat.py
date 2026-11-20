from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.services import conversation_service
from app.services.assistant_service import AssistantNotAvailableError, require_available_assistant
from app.services.llm_service import LLMServiceError, ensure_provider_is_configured, generate_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def send_chat_message(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be blank.")
    try:
        assistant = require_available_assistant(request.assistant_id)
    except AssistantNotAvailableError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Do not create an empty conversation when the provider is not configured.
    try:
        ensure_provider_is_configured()
    except LLMServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    if request.conversation_id:
        conversation = conversation_service.get_conversation(request.conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        if conversation["assistant_id"] != assistant.id:
            raise HTTPException(
                status_code=400,
                detail="Choose the assistant already used by this conversation, or start a new chat.",
            )
    else:
        title = " ".join(request.message.split())[:72]
        conversation = conversation_service.create_conversation(assistant.id, title)

    prior_messages = conversation_service.list_messages(conversation["id"])
    user_message = request.message.strip()
    conversation_service.add_message(conversation["id"], "user", user_message)

    context = [
        {"role": item["role"], "content": item["content"]}
        for item in prior_messages[-settings.max_context_messages :]
    ]
    context.append({"role": "user", "content": user_message})

    try:
        answer = generate_reply(assistant, context)
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"message": str(exc), "conversation_id": conversation["id"]},
        ) from exc

    saved_answer = conversation_service.add_message(conversation["id"], "assistant", answer)
    return ChatResponse(
        conversation_id=conversation["id"],
        assistant_id=assistant.id,
        title=conversation["title"],
        message=answer,
        created_at=saved_answer["created_at"] or datetime.now(timezone.utc),
    )
