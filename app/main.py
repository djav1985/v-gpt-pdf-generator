# main.py
import os
from contextlib import asynccontextmanager
from pathlib import Path as FilePath
from typing import Generator

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.openapi.utils import get_openapi

from .routes.create import pdf_router
from .models import ErrorResponse
from .dependencies import cleanup_downloads_folder

tags_metadata = [
    {"name": "PDF", "description": "Operations for creating PDF documents."}
]

@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, Any, None]:
    downloads_path = FilePath("/app/downloads")
    downloads_path.mkdir(parents=True, exist_ok=True)
    await cleanup_downloads_folder(str(downloads_path))
    try:
        yield
    finally:
        await cleanup_downloads_folder(str(downloads_path))

# FastAPI application instance
app = FastAPI(
    lifespan=lifespan,
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    openapi_tags=tags_metadata,
    root_path=os.getenv("ROOT_PATH", ""),
    root_path_in_servers=False,
    servers=[
        {
            "url": f"{os.getenv('BASE_URL', '')}{os.getenv('ROOT_PATH', '')}",
            "description": "Base API server",
        }
    ]
)

# Including Routers for different endpoints
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
    filename: str = Path(..., description="Name of the PDF file to download", example="example.pdf")
) -> FileResponse:
    downloads_dir = FilePath("/app/downloads").resolve()
    file_path = FilePath("/app/downloads", filename).resolve()
    if not str(file_path).startswith(str(downloads_dir)):
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
    security_scheme = (
        openapi_schema.get("components", {})
        .get("securitySchemes", {})
        .get("HTTPBearer", {})
    )
    if security_scheme:
        security_scheme["description"] = "Provide the API key as a Bearer token"
        security_scheme["bearerFormat"] = "API Key"
    openapi_schema["openapi"] = "3.1.0"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
