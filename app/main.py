# main.py
import os  # Used for accessing environment variables

from fastapi import FastAPI, HTTPException, Security
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

# Importing local modules
from functions import AppConfig

from routes.create import pdf_router
from routes.dify import dify_router
from routes.root import root_router

# Load configuration on startup
config = AppConfig()

# Setup the bearer token authentication scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    if config.API_KEY and (
        not credentials or credentials.credentials != config.API_KEY
    ):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return credentials.credentials if credentials else None


# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    servers=[{"url": f"{config.KB_BASE_URL}", "description": "Base API server"}],
)

# Including Routers for different endpoints
app.include_router(pdf_router)

# Conditionally include the root_router based on EMBEDDING_ENDPOINT env var
if os.getenv("DIFY") == "true":
    app.include_router(dify_router)

# Including Routers for different endpoints
app.include_router(root_router)

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
