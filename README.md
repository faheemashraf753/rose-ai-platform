# ROSE — Modular Multi-Assistant AI Platform

ROSE is a full-stack AI workspace for general questions and programming help. It is built as a B.Tech CSE major project with a small, understandable architecture: HTML, CSS, and Vanilla JavaScript in the browser; Python and FastAPI on the backend; MySQL for conversation storage; and a modular Gemini service.

## Problem statement

People often switch between separate tools for coding, learning, research, and writing. ROSE explores a unified workspace where purpose-built assistants share a consistent interface and conversation history.

## Objectives

- Provide one workspace for specialized assistants.
- Keep each assistant's purpose and system instructions separate.
- Save conversations in a relational database.
- Keep AI credentials on the backend.
- Make later assistant additions possible without replacing the frontend stack.

## V1 features

- Responsive dashboard with assistant cards, prompt suggestions, status, recent conversations, settings, and team information.
- General and Coding assistant chat flows using the same configured Gemini model with different instructions when an API key is available.
- FastAPI health, assistant, chat, and conversation endpoints.
- MySQL persistence for conversations and messages.
- Clear missing-key, database, and provider error states.
- Research and Document assistants are visible as planned capabilities and cannot be selected for chat.

Saved Notes, login, file uploads, Research, and Document analysis are planned rather than implemented.

## Technology stack

- HTML5, CSS3, and Vanilla JavaScript modules.
- Python 3.11, FastAPI, Uvicorn, Pydantic.
- MySQL 8.0 and mysql-connector-python.
- Gemini API through a backend-only HTTP service.

## Project structure

~~~text
.
|-- frontend/
|   |-- index.html
|   |-- css/style.css
|   |-- js/{main,api,assistants,chat}.js
|-- backend/
|   |-- requirements.txt
|   |-- app/
|   |   |-- main.py, config.py
|   |   |-- assistants/{registry,instructions}.py
|   |   |-- database/connection.py
|   |   |-- models/schemas.py
|   |   |-- routes/{health,assistants,chat,conversations}.py
|   |   |-- services/{assistant_service,conversation_service,llm_service}.py
|   |-- tests/test_assistant_registry.py
|-- database/schema.sql
|-- docs/{PROJECT_REQUIREMENTS,ARCHITECTURE}.md
|-- .env.example
|-- .gitignore
|-- README.md
~~~

## Prerequisites

- Python 3.11.
- MySQL Server 8.0 running locally.
- A Gemini API key for real AI responses. ROSE does not include a key or assume that paid credits are available.

## Installation and run

Run these commands from the ROSE project root in PowerShell:

~~~powershell
Copy-Item .env.example .env
py -3.11 -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
python -m pip install -r backend/requirements.txt
~~~

Edit .env and set the MySQL host, port, database user, and password for your local MySQL installation. The example uses the local root account with a blank password; replace that value with your own local setting.

Create only the ROSE database and tables by importing the supplied schema:

~~~powershell
Get-Content -Raw database/schema.sql | mysql -u root -p
~~~

Enter the password for your local MySQL account when prompted. The schema creates rose_db and does not alter another database.

For real Gemini replies, add your Gemini API key to AI_API_KEY in the root .env file. Keep that file private and restart the backend after changes. The default model is configured through AI_MODEL and can be changed there. No provider request is sent while AI_API_KEY is blank.

Start FastAPI from the backend directory:

~~~powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
~~~

Open http://127.0.0.1:8000 in a browser. The same server hosts the frontend and API. FastAPI's interactive API documentation is at http://127.0.0.1:8000/docs.

If you prefer serving static files separately, start the API first, then in another terminal run:

~~~powershell
python -m http.server 5500 --directory frontend
~~~

Open http://127.0.0.1:5500. The local development origins are included in FRONTEND_ORIGINS.

## API overview

- GET /api/health
- GET /api/assistants
- POST /api/chat
- GET /api/conversations?limit=20
- GET /api/conversations/{conversation_id}
- GET /api/conversations/{conversation_id}/messages
- DELETE /api/conversations/{conversation_id}

A chat request contains assistant_id, message, and an optional conversation_id. The backend validates the request, loads recent messages from MySQL, calls Gemini, and saves the response.

## Configuration and data

The .env.example file documents database and Gemini settings. Copy it to .env and fill in local values. Never put AI_API_KEY into HTML or frontend JavaScript. .gitignore excludes .env.

ROSE sends chat prompts and the bounded conversation history to the Gemini API when a valid key is configured. Review Google's current Gemini API terms and data controls before using sensitive content.

The backend adapter follows Google's [GenerateContent API reference](https://ai.google.dev/api/generate-content). The example model is listed in the [Gemini 3.8 Flash reference](https://aistudio.google.com/docs/models/gemini-3.8-flash). A live Gemini response has not been verified in this workspace because no API key is configured.

## Screenshots

No screenshots are included yet. Capture dashboard and mobile screenshots after running the app with the local services configured.

## Team

- Project Leader: Faheem Ul Islam Rather
- Co-Leader: Mir Adnan Ishtiyaq
- Team Member: Mir Ibrahim

No individual contributions or performance results are assumed here.

## Future enhancements

Authentication, Saved Notes, Research and Document assistants, Career and Study assistants, file uploads, streaming output, usage controls, and deployment hardening are possible follow-on releases.

## Verification

Run the registry unit checks from the backend directory:

~~~powershell
python -m unittest discover -s tests
~~~

The full acceptance flow also needs MySQL 8.0 and a valid Gemini configuration. Do not describe AI replies or database persistence as verified until those services have been exercised.
