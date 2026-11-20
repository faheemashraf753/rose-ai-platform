"""Gemini HTTP adapter. This module is the only place that calls the provider."""

import logging
import re
import time

import httpx

from app.assistants.registry import Assistant
from app.config import settings


logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Maximum number of attempts, including the first request.
MAX_RETRIES = 4

# Waiting time before each retry.
RETRY_DELAYS = [1, 2, 4]

# Temporary Gemini server errors.
RETRYABLE_STATUS_CODES = (500, 502, 503, 504)

# Maximum time allowed for one Gemini request.
REQUEST_TIMEOUT = 60.0


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


def wait_before_retry(attempt: int) -> None:
    """Wait before sending another request."""

    wait_time = RETRY_DELAYS[attempt]

    logger.warning(
        "Waiting %s seconds before retrying Gemini. Attempt %s of %s.",
        wait_time,
        attempt + 2,
        MAX_RETRIES,
    )

    time.sleep(wait_time)


def send_gemini_request(endpoint: str, body: dict) -> httpx.Response:
    """Send a Gemini request with automatic retries."""

    for attempt in range(MAX_RETRIES):

        try:
            response = httpx.post(
                endpoint,
                headers={
                    "x-goog-api-key": settings.ai_api_key,
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=REQUEST_TIMEOUT,
            )

        # Handle request timeouts.
        except httpx.TimeoutException:

            logger.warning(
                "Gemini request timed out. Attempt %s of %s.",
                attempt + 1,
                MAX_RETRIES,
            )

            if attempt < MAX_RETRIES - 1:
                wait_before_retry(attempt)
                continue

            raise LLMServiceError(
                "Gemini is taking too long to respond. "
                "ROSE tried several times but could not get an answer. "
                "Please wait a moment and try again.",
                status_code=504,
            )

        # Handle temporary connection problems.
        except httpx.ConnectError:

            logger.warning(
                "Could not connect to Gemini. Attempt %s of %s.",
                attempt + 1,
                MAX_RETRIES,
            )

            if attempt < MAX_RETRIES - 1:
                wait_before_retry(attempt)
                continue

            raise LLMServiceError(
                "ROSE could not connect to Gemini after several attempts. "
                "Check your internet connection and try again.",
                status_code=503,
            )

        # Handle other network errors.
        except httpx.RequestError as exc:

            logger.error(
                "Gemini network error: %s",
                type(exc).__name__,
            )

            raise LLMServiceError(
                "ROSE encountered a network problem while contacting Gemini. "
                "Please try again.",
                status_code=502,
            ) from exc

        # Handle temporary Gemini server errors.
        if response.status_code in RETRYABLE_STATUS_CODES:

            logger.warning(
                "Gemini returned HTTP %s. Attempt %s of %s.",
                response.status_code,
                attempt + 1,
                MAX_RETRIES,
            )

            if attempt < MAX_RETRIES - 1:
                wait_before_retry(attempt)
                continue

            logger.error(
                "Gemini failed after %s attempts. "
                "HTTP %s | Response: %s",
                MAX_RETRIES,
                response.status_code,
                response.text[:1000],
            )

            raise LLMServiceError(
                "Gemini is temporarily unavailable or experiencing "
                "high demand. ROSE tried several times but could not "
                "get a response. Please try again shortly.",
                status_code=503,
            )

        # Return successful responses and non-retryable errors.
        return response

    raise LLMServiceError(
        "Gemini could not complete your request. Please try again."
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

    # Send the request with automatic retries.
    response = send_gemini_request(endpoint, body)

    # Handle rate limits.
    if response.status_code == 429:
        logger.warning("Gemini rate limit reached.")

        raise LLMServiceError(
            "Gemini rate limit reached. Wait a moment, then try again.",
            status_code=429,
        )

    # Handle authentication errors.
    if response.status_code in (401, 403):
        logger.error(
            "Gemini authentication failed: HTTP %s",
            response.status_code,
        )

        raise LLMServiceError(
            "Gemini rejected the API key or its permissions. "
            "Check the key in .env and your Google AI Studio setup.",
            status_code=response.status_code,
        )

    # Handle invalid requests.
    if response.status_code == 400:
        logger.error(
            "Gemini rejected the request: %s",
            response.text[:1000],
        )

        raise LLMServiceError(
            "Gemini rejected this request. "
            "Check AI_MODEL and try a shorter or differently worded message.",
            status_code=400,
        )

    # Handle other HTTP errors.
    if response.is_error:
        logger.error(
            "Gemini returned HTTP %s | Response: %s",
            response.status_code,
            response.text[:1000],
        )

        raise LLMServiceError(
            "Gemini could not complete the request. Please try again.",
            status_code=response.status_code,
        )

    # Extract the AI response.
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

