# main.py
import os

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.openapi.utils import get_openapi

from .routes.create import pdf_router
from .models import ErrorResponse

tags_metadata = [
    {"name": "PDF", "description": "Operations for creating PDF documents."}
]

# FastAPI application instance
app = FastAPI(
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
    "/downloads/{filename}",
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
async def download_pdf(
    filename: str = Path(..., description="Name of the PDF file to download", example="example.pdf")
):
    file_path = f"/app/downloads/{filename}"
    if not os.path.isfile(file_path):
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
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
