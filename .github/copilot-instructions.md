# Copilot Instructions for AI Coding Agents

## Project Overview
- This is a FastAPI-based microservice for generating PDFs from HTML, with asynchronous processing and Docker-based deployment.
- Key files: `app/main.py` (FastAPI app entry), `app/routes/create.py` (PDF creation endpoint), `app/dependencies.py` (PDF generation logic, API key validation), `app/models.py` (request/response models).
- PDF generation uses WeasyPrint; requests are POSTed to `/` with JSON payloads, and results are served from `/downloads`.

## Architecture & Data Flow
- **Entry point:** `app/main.py` initializes FastAPI, mounts static files, and includes routes.
- **PDF creation:** `app/routes/create.py` handles POST requests, validates API keys, and calls PDF generation logic in `app/dependencies.py`.
- **Models:** `app/models.py` defines Pydantic models for request validation.
- **Downloads:** Generated PDFs are saved to a static folder and served via `/downloads`.
- **Security:** API key required for PDF creation; validated in dependencies.

## Developer Workflows
- **Run locally:**
  - Use Docker Compose: `docker-compose up` (or `-d` for detached mode).
  - Service runs on port 8888 by default.
- **Configuration:**
  - Set environment variables in `docker-compose.yml` (e.g., `BASE_URL`, `API_KEY`, `WORKERS`).
- **API usage:**
  - POST to `/` with JSON body (see README for example payload).
  - Download PDFs from `/downloads`.
- **OpenAPI docs:**
  - Available at `/openapi.json` for integration/testing.

## Conventions & Patterns
- **Modular structure:**
  - All business logic is separated into `app/dependencies.py`.
  - Routing is in `app/routes/`, models in `app/models.py`.
- **Error handling:**
  - API key errors and PDF generation exceptions are handled with clear responses.
- **Code style:**
  - Follows PEP 8, with clear variable names and modular functions.
- **Documentation:**
  - Update `README.md` and `CHANGELOG.md` for any public-facing changes (see `AGENTS.md` for doc sync policy).

## Integration Points
- **External libraries:**
  - FastAPI, WeasyPrint, Pydantic, aiohttp, aiofiles, uvicorn.
- **Containerization:**
  - Dockerfile and docker-compose.yml define build/run environment.

## Project-Specific Guidance
- No automated test suite is present; add tests in a dedicated test directory if contributing.
- Always sync documentation across `README.md`, `CHANGELOG.md`, and other public docs.
- Reference `AGENTS.md` for contributor workflow and code quality expectations.

---

## Example: PDF Generation Request
```json
{
  "pdf_title": "Example",
  "body_content": "<p>Hello</p>",
  "contains_code": false,
  "css_content": "p { color: blue; }",
  "output_filename": "example"
}
```

---

For questions about architecture, workflows, or conventions, see `README.md` and `AGENTS.md`.
