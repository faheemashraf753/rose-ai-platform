"""Small service wrapper around the assistant registry."""
from app.assistants.registry import get_assistant, list_assistants


class AssistantNotAvailableError(ValueError):
    pass


def public_assistants() -> list[dict]:
    return [assistant.public_data() for assistant in list_assistants()]


def require_available_assistant(assistant_id: str):
    assistant = get_assistant(assistant_id)
    if assistant is None:
        raise AssistantNotAvailableError("Choose a valid ROSE assistant.")
    if not assistant.available:
        raise AssistantNotAvailableError(
            f"{assistant.name} is planned and is not available in this release."
        )
    return assistant
