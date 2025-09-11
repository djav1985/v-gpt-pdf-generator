# main.py
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes.create import pdf_router

tags_metadata = [
    {"name": "PDF", "description": "Operations for creating PDF documents."}
]

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    root_path=os.getenv("ROOT_PATH", "/"),
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

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")
