# Importing necessary modules and libraries
import os
import time
import asyncio
import random
import string
import aiohttp

from aiohttp import ClientSession
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from weasyprint import HTML, CSS


# Importing local modules
from functions import AppConfig, generate_pdf, convert_url_to_pdf_task, cleanup_downloads_folder, submit_to_kb, scrape_site

# Load configuration on startup
config = AppConfig()

# Setup the bearer token authentication scheme
bearer_scheme = HTTPBearer(auto_error=False)

async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if config.API_KEY and (not credentials or credentials.credentials != config.API_KEY):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return credentials.credentials if credentials else None

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    servers=[{"url": config.BASE_URL, "description": "Base API server"}]
)

# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    html_content: str = Field(..., description="HTML content that will be converted into a PDF document.")
    css_content: Optional[str] = Field(default="body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }", description="Optional CSS content for styling the HTML.")
    output_filename: Optional[str] = Field(..., description="Optional filename, use - for spaces and do not include the extension.")

# Request model for converting a single URL to PDF
class ConvertURLRequest(BaseModel):
    url: str = Field(..., description="URL to be converted into a PDF. The URL should return HTML content that can be rendered into a PDF.")

# Endpoint for creating a new PDF
@app.post("/create", operation_id="create_pdf")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):

    background_tasks.add_task(cleanup_downloads_folder, "/app/downloads/")

    # Use provided CSS or the default
    css_content = request.css_content

    if request.output_filename is None:
        # Generate a filename with random characters and datetime
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
        request.output_filename = f"{random_chars}-{datetime_suffix}.pdf"
    else:
        # Append datetime to provided filename
        datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
        request.output_filename += f"-{datetime_suffix}.pdf"

    output_path = Path("/app/downloads") / request.output_filename
    # Start the background task to generate the PDF
    background_tasks.add_task(generate_pdf, html_content=request.html_content, css_content=css_content, output_path=output_path)

    # Check if there was an exception during PDF generation
    if "exception" in background_tasks:
        return JSONResponse(status_code=500, content={"message": "PDF generation failed. Please try again later.", "exception": background_tasks["exception"]})

    # Wait for the file to exist (with timeout)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 5:
            pdf_url = f"{BASE_URL}/downloads/{request.output_filename}"
            return JSONResponse(status_code=202, content={"message": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

    return FileResponse(path=output_path, filename=request.output_filename, media_type='application/pdf')

# Endpoint for converting URLs to PDFs
@app.post("/convert_urls", operation_id="url_to_pdf")
async def convert_url_to_pdf(request: ConvertURLRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):

    background_tasks.add_task(cleanup_downloads_folder, "/app/downloads/")

    # Fetch the URL from the request
    url = request.url.strip()

    datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    output_filename = f"url-{datetime_suffix}.pdf"
    output_path = Path("/app/downloads") / output_filename

    # Start background task to convert the URL to PDF
    background_tasks.add_task(
        convert_url_to_pdf_task,
        url=url,
        output_path=output_path
    )

    # Check if there was an exception during PDF generation
    if "exception" in background_tasks:
        return JSONResponse(status_code=500, content={"message": "PDF generation failed. Please try again later.", "exception": background_tasks["exception"]})

    # Wait for the file to exist (with timeout)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 10:
            pdf_url = f"{BASE_URL}/downloads/{output_filename}"
            return JSONResponse(status_code=202, content={"message": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

    return FileResponse(path=output_path, filename=output_filename, media_type='application/pdf')

if config.DIFY:

    class KBCreationRequest(BaseModel):
        """Model for creating a Knowledge Base."""
        name: str = Field(..., description="Name of the knowledge base to be created.")

    class KBSubmissionRequest(BaseModel):
        """Model for submitting a document."""
        website_url: str = Field(..., description="URL of the website to scrape.")
        dataset_id: str = Field(..., description="ID of the dataset to submit the document to.")
        indexing_technique: Optional[str] = Field("high_quality", description="Indexing technique to be used.")

    @app.post("/create-kb/", operation_id="create_kb")
    async def create_new_kb(request: KBCreationRequest, api_key: str = Depends(get_api_key)):
        api_url = f"{config.KB_BASE_URL}/v1/datasets"
        headers = {
            "Authorization": f"Bearer {config.KB_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"name": request.name}
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="API request failed to create the KB.")
        return JSONResponse(status_code=200, content={"message": f"Knowledge Base {request.name} created successfully."})

    @app.post("/kb-scraper/")
    async def scrape_to_kb(request: KBSubmissionRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
        async with ClientSession() as session:
            await scrape_site(request.website_url, session, request.unwanted_extensions, background_tasks, request.dataset_id, request.indexing_technique)
        return {"message": f"Scraping {request.website_url} to Knowledge Base {request.dataset_id} initiated. Check dataset for updates."}

# Root endpoint serving index.html directly
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("/app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
