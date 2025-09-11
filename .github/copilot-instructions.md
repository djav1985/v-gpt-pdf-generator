
# Copilot Instructions for AI Coding Agents

## Project Overview
- **Purpose:** FastAPI microservice for generating PDFs from HTML, designed for async processing and containerized deployment.
- **Key files:**
  - `app/main.py`: FastAPI app entry, mounts static files, includes routes.
  - `app/routes/create.py`: Handles PDF creation endpoint, POST requests, API key validation.
  - `app/dependencies.py`: Contains PDF generation logic (WeasyPrint), API key validation, and business logic.
  - `app/models.py`: Pydantic models for request/response validation.
  - `tests/`: Pytest-based tests for dependencies and routes.

## Architecture & Data Flow
- **Startup:**
  - `main.py` initializes FastAPI, mounts `/downloads` for static PDF serving, and includes route modules.
- **PDF Generation:**
  - POST to `/` with JSON payload triggers PDF creation (see example below).
  - API key is required and validated in dependencies.
  - PDF is generated asynchronously and saved to a static folder, accessible via `/downloads/{filename}`.
- **Models:**
  - All request/response schemas are defined in `models.py` for strict validation.

## Developer Workflows
- **Run locally:**
  - Use Docker Compose: `docker-compose up` (or `-d` for detached mode). Default port: 8888.
  - Environment variables (e.g., `BASE_URL`, `API_KEY`, `WORKERS`) are set in `docker-compose.yml`.
- **Testing:**
  - Run tests with `pytest tests/` (see `AGENTS.md` for test policy).
- **Linting:**
  - Use PEP 8 style; run `flake8 app/ tests/` for lint checks.
- **API usage:**
  - POST to `/` with JSON body (see below). Download PDFs from `/downloads`.
- **Docs:**
  - OpenAPI spec at `/openapi.json`.

## Conventions & Patterns
- **Modular structure:**
  - Business logic in `dependencies.py`, routing in `routes/`, models in `models.py`.
- **Error handling:**
  - API key and PDF generation errors return clear JSON responses.
- **Documentation sync:**
  - Always update `README.md`, `CHANGELOG.md`, and public docs together (see `AGENTS.md`).
- **Tests:**
  - All new features/bugfixes require or update tests in `tests/`.

## Integration Points
- **External libraries:** FastAPI, WeasyPrint, Pydantic, aiohttp, aiofiles, uvicorn.
- **Containerization:** Dockerfile and docker-compose.yml define build/run environment.

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

## References
- For architecture, workflows, or conventions, see `README.md` and `AGENTS.md`.
