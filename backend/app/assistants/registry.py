"""The assistant registry is the single source for IDs and availability."""
from dataclasses import asdict, dataclass

from app.assistants.instructions import (
    CODING_INSTRUCTIONS,
    DOCUMENT_INSTRUCTIONS,
    GENERAL_INSTRUCTIONS,
    RESEARCH_INSTRUCTIONS,
)


@dataclass(frozen=True)
class Assistant:
    id: str
    name: str
    description: str
    instructions: str
    capabilities: tuple[str, ...]
    available: bool
    icon: str

    def public_data(self) -> dict:
        data = asdict(self)
        data.pop("instructions")
        data["capabilities"] = list(self.capabilities)
        return data


_ASSISTANTS = (
    Assistant(
        id="general",
        name="General Assistant",
        description="Everyday questions, clear explanations, and practical help.",
        instructions=GENERAL_INSTRUCTIONS,
        capabilities=("Everyday questions", "Explanations", "General tasks", "Conversation"),
        available=True,
        icon="spark",
    ),
    Assistant(
        id="coding",
        name="Coding Assistant",
        description="Understand code, work through errors, and build better solutions.",
        instructions=CODING_INSTRUCTIONS,
        capabilities=("Programming help", "Debugging", "Code review", "Learning"),
        available=True,
        icon="code",
    ),
    Assistant(
        id="research",
        name="Research Assistant",
        description="A future space for guided research and source discovery.",
        instructions=RESEARCH_INSTRUCTIONS,
        capabilities=("Research planning", "Source discovery"),
        available=False,
        icon="search",
    ),
    Assistant(
        id="document",
        name="Document Assistant",
        description="A future space for understanding and summarizing documents.",
        instructions=DOCUMENT_INSTRUCTIONS,
        capabilities=("Document understanding", "Summaries"),
        available=False,
        icon="document",
    ),
)

ASSISTANTS = {assistant.id: assistant for assistant in _ASSISTANTS}


def list_assistants() -> list[Assistant]:
    return list(_ASSISTANTS)


def get_assistant(assistant_id: str) -> Assistant | None:
    return ASSISTANTS.get(assistant_id)
