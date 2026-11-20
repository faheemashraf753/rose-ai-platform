"""Gemini HTTP adapter. This module is the only place that calls the provider."""

import logging
import re

import httpx

from app.assistants.registry import Assistant
from app.config import settings


logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class LLMServiceError(RuntimeError):
    """Raised when the AI provider cannot complete a request."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def ensure_provider_is_configured() -> None:
    """Validate Gemini configuration before making an API request."""

    if settings.ai_provider != "gemini":
        raise LLMServiceError(
            "ROSE is configured for Gemini. "
            "Set AI_PROVIDER=gemini in .env to continue.",
            status_code=503,
        )

    if not settings.ai_api_key:
        raise LLMServiceError(
            "Gemini is selected, but AI_API_KEY is empty. "
            "Add your key to the root .env file and restart FastAPI.",
            status_code=503,
        )

    if not re.fullmatch(r"[A-Za-z0-9._-]+", settings.ai_model):
        raise LLMServiceError(
            "AI_MODEL contains unsupported characters. "
            "Check the model name in .env.",
            status_code=503,
        )


def generate_reply(assistant: Assistant, messages: list[dict]) -> str:
    """Send conversation messages to Gemini and return its response."""

    ensure_provider_is_configured()

    contents = [
        {
            "role": "model" if item["role"] == "assistant" else "user",
            "parts": [{"text": item["content"]}],
        }
        for item in messages
    ]

    body = {
        "systemInstruction": {
            "parts": [{"text": assistant.instructions}]
        },
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 2048
        },
    }

    endpoint = (
        f"{GEMINI_API_BASE}/{settings.ai_model}:generateContent"
    )

    try:
        response = httpx.post(
            endpoint,
            headers={
                "x-goog-api-key": settings.ai_api_key,
                "Content-Type": "application/json",
            },
            json=body,
            timeout=45.0,
        )

    except httpx.TimeoutException as exc:
        logger.warning("Gemini request timed out.")

        raise LLMServiceError(
            "Gemini took too long to respond. Please try again."
        ) from exc

    except httpx.RequestError as exc:
        logger.warning(
            "Could not connect to Gemini: %s",
            type(exc).__name__,
        )

        raise LLMServiceError(
            "ROSE could not connect to Gemini. "
            "Check your internet connection and try again."
        ) from exc

    # Handle rate limits
    if response.status_code == 429:
        logger.warning("Gemini rate limit reached.")

        raise LLMServiceError(
            "Gemini rate limit reached. Wait a moment, then try again.",
            status_code=429,
        )

    # Handle authentication errors
    if response.status_code in (401, 403):
        logger.error(
            "Gemini authentication failed: HTTP %s",
            response.status_code,
        )

        raise LLMServiceError(
            "Gemini rejected the API key or its permissions. "
            "Check the key in .env and your Google AI Studio setup."
        )

    # Handle invalid requests
    if response.status_code == 400:
        logger.error(
            "Gemini rejected the request: %s",
            response.text[:1000],
        )

        raise LLMServiceError(
            "Gemini rejected this request. "
            "Check AI_MODEL and try a shorter or differently worded message."
        )

    # Handle Gemini server errors
    if response.status_code >= 500:
        logger.error(
            "Gemini server error: HTTP %s | Response: %s",
            response.status_code,
            response.text[:1000],
        )

        raise LLMServiceError(
            "Gemini is temporarily unavailable. Please try again shortly."
        )

    # Handle other HTTP errors
    if response.is_error:
        logger.error(
            "Gemini returned HTTP %s | Response: %s",
            response.status_code,
            response.text[:1000],
        )

        raise LLMServiceError(
            "Gemini could not complete the request. Please try again."
        )

    # Extract the AI response
    try:
        payload = response.json()

        parts = payload["candidates"][0]["content"]["parts"]

        answer = "\n".join(
            part["text"]
            for part in parts
            if isinstance(part.get("text"), str)
        ).strip()

    except (ValueError, KeyError, IndexError, TypeError):
        answer = ""

    if not answer:
        logger.warning(
            "Gemini returned an empty or invalid response."
        )

        raise LLMServiceError(
            "Gemini did not return a text response. "
            "Try rephrasing your message."
        )

    return answer
