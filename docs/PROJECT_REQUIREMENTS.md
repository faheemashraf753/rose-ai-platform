# ROSE V1 Project Requirements

## Purpose

ROSE is a modular multi-assistant workspace for a B.Tech Computer Science and Engineering major project. It brings specialized AI help into one application while keeping each assistant's instructions and availability explicit.

## V1 scope

### Included

- Responsive dashboard with Home, My Crew, Activity, Conversations, Settings, About, and Project Team interactions.
- General Assistant and Coding Assistant, backed by the same configured Gemini model with different system instructions.
- FastAPI endpoints for health, assistant metadata, chat, and conversation history.
- MySQL storage for assistant metadata, conversations, and messages.
- Server-side provider credentials, request validation, request size limits, friendly API errors, and parameterized SQL.
- New conversation creation on the first chat request and history retrieval from MySQL.

### Planned

- Research and Document assistants, shown in the interface but unavailable for chat.
- Authentication, multiple user accounts, Saved Notes, uploads, Career Assistant, Study Assistant, Writing Assistant, and Finance Assistant.
- Streaming responses and production deployment hardening.

## Functional requirements

1. Users can choose General or Coding before starting a conversation.
2. The backend selects the assistant's instructions from the assistant registry.
3. The backend sends chat history and the current user message to Gemini only when a key is configured.
4. User and assistant messages are persisted in the same MySQL conversation.
5. The user can reopen and delete a saved conversation through the API.
6. Missing API configuration, provider failures, and MySQL failures return clear errors.
7. Assistant cards identify planned capabilities and do not submit requests for them.
8. The frontend uses plain HTML, CSS, and JavaScript modules; no frontend framework is used.

## Technology decisions

- Frontend: HTML5, CSS3, Vanilla JavaScript modules.
- Backend: Python 3.11, FastAPI, Uvicorn.
- Database: MySQL 8.0 using parameterized mysql-connector-python queries.
- AI provider: Google Gemini through a backend-only HTTP adapter. The model is configurable in .env.
- The V1 demo is single-user and does not claim production-grade security.

## Acceptance status

Acceptance checks are not claimed as passed until the frontend, backend, MySQL, and a configured Gemini key have been exercised together. See the root README for setup and current prerequisites.
