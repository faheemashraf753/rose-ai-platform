# ROSE V1 Architecture

## Request flow

1. The browser loads the static dashboard from FastAPI (or a separate local static server).
2. Vanilla JavaScript calls the same-origin /api endpoints.
3. FastAPI validates request shapes with Pydantic and routes work to assistant, conversation, and LLM services.
4. The assistant registry selects assistant-specific instructions and marks unavailable assistants as planned.
5. Conversation and message services use parameterized MySQL statements.
6. The Gemini adapter is called only on the backend and only when AI_PROVIDER and AI_API_KEY are configured.

## Modules

- frontend/index.html: semantic dashboard structure and dialogs.
- frontend/css/style.css: layout, design system, and responsive breakpoints.
- frontend/js/api.js: fetch wrapper and user-facing API errors.
- frontend/js/assistants.js: assistant list and card rendering.
- frontend/js/chat.js: chat requests and safe message rendering.
- frontend/js/main.js: page state, navigation, conversations, dialogs, and health status.
- backend/app/assistants: assistant definitions and separate system instructions.
- backend/app/routes: API endpoints and HTTP behavior.
- backend/app/services: assistant selection, Gemini calls, and conversation use cases.
- backend/app/database: MySQL connection handling.
- backend/app/models: Pydantic request and response schemas.
- database/schema.sql: the new rose_db schema and V1 assistant seed records.

## Conversation behavior

The first chat message creates a conversation, then persists the user message and generated assistant response. Later messages load prior content from MySQL and include a bounded recent history in the Gemini request. If Gemini fails after the user message is saved, the API error includes the conversation ID so the client can keep and retry in that conversation.

Gemini requests use Google's GenerateContent REST API. ROSE stores the product conversation in MySQL; API data handling is also subject to Google's Gemini API terms and data controls.

## Boundaries

- V1 is a single-user local demonstration and has no authentication or per-user authorization.
- The backend never executes submitted code.
- Research and Document assistants are not functional in this release.
- AI responses require a valid Gemini API key and model access. No API key is included in the repository.
