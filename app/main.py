"""Application entry point configuring routes and startup behavior."""

from contextlib import asynccontextmanager
from pathlib import Path as FilePath
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse

from .config import settings
from .dependencies import cleanup_downloads_folder
from .models import ErrorResponse
from .routes.create import pdf_router

tags_metadata = [
    {"name": "PDF", "description": "Operations for creating PDF documents."}
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    downloads_path = FilePath("/app/downloads")
    downloads_path.mkdir(parents=True, exist_ok=True)
    await cleanup_downloads_folder(str(downloads_path))
    try:
        yield
    finally:
        await cleanup_downloads_folder(str(downloads_path))

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    openapi_version="3.1.0",
    openapi_tags=tags_metadata,
    root_path=settings.ROOT_PATH,
    root_path_in_servers=False,
    servers=[
        {
            "url": f"{settings.BASE_URL}{settings.ROOT_PATH}",
            "description": "Base API server",
        }
    ],
    lifespan=lifespan,
)

# Include routers
app.include_router(pdf_router)


@app.get(
    "/downloads/{filename:path}",
    response_class=FileResponse,
    tags=["PDF"],
    summary="Download PDF",
    description="Retrieve a previously generated PDF file by its filename.",
    responses={
        404: {"description": "File not found", "model": ErrorResponse},
    },
    openapi_extra={
        "responses": {
            "404": {
                "content": {
                    "application/json": {
                        "example": {
                            "status": 404,
                            "code": "file_not_found",
                            "message": "File not found",
                            "details": "Ensure the filename is correct",
                        }
                    }
                }
            }
        }
    },
)
def download_pdf(
    filename: str = Path(
        ...,
        description="Name of the PDF file to download",
        example="example.pdf"
    )
) -> FileResponse:
    downloads_dir = FilePath("/app/downloads").resolve()
    file_path = (downloads_dir / filename).resolve()
    try:
        file_path.relative_to(downloads_dir)
    except ValueError:
        raise HTTPException(status_code=400)
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "status": 404,
                "code": "file_not_found",
                "message": "File not found",
                "details": "Ensure the filename is correct",
            },
        )
    return FileResponse(file_path)


def custom_openapi() -> dict:
    """Generate and cache a custom OpenAPI schema for the app."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
        servers=app.servers,
    )
    # Update API key authentication scheme metadata
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    api_key_scheme = security_schemes.get("APIKeyHeader")
    if api_key_scheme is None:
        api_key_scheme = security_schemes.setdefault(
            "APIKeyHeader",
            {"type": "apiKey", "name": "X-API-Key", "in": "header"},
        )
    api_key_scheme["description"] = "Provide the API key via the X-API-Key header"
    openapi_schema["openapi"] = "3.1.0"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return JSON errors for HTTPException instances."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
