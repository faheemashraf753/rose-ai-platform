from fastapi import APIRouter

from app.models.schemas import AssistantResponse
from app.services.assistant_service import public_assistants

router = APIRouter()


@router.get("/assistants", response_model=list[AssistantResponse])
def get_assistants() -> list[dict]:
    return public_assistants()
