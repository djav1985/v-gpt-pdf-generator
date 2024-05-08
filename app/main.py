# main.py
import os

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Security
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import FileResponse

from routes.create import pdf_router
from routes.root import root_router


# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    servers=[{"url": f"{config.KB_BASE_URL}", "description": "Base API server"}],
)

# Including Routers for different endpoints
app.include_router(pdf_router)

# Including Routers for different endpoints
app.include_router(root_router)

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
