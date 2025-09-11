# main.py
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi

from .routes.create import pdf_router

tags_metadata = [
    {"name": "PDF", "description": "Operations for creating PDF documents."}
]

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    root_path=os.getenv("ROOT_PATH", ""),
    root_path_in_servers=False,
    servers=[
        {
            "url": f"{os.getenv('BASE_URL', '')}{os.getenv('ROOT_PATH', '/')}",
            "description": "Base API server",
        }
    ],
    contact={
        "name": "Project Support",
        "url": "https://example.com/contact",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://example.com/terms",
    openapi_tags=tags_metadata,
)

# Including Routers for different endpoints
app.include_router(pdf_router)


@app.get("/downloads/{filename}", response_class=FileResponse, tags=["PDF"])
async def download_pdf(filename: str):
    file_path = f"/app/downloads/{filename}"
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    security_scheme = (
        openapi_schema.get("components", {})
        .get("securitySchemes", {})
        .get("HTTPBearer", {})
    )
    if security_scheme:
        security_scheme["description"] = "Provide the API key as a Bearer token"
        security_scheme["bearerFormat"] = "API Key"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
