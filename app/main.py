# Importing necessary modules and libraries
import os
import re
import time
import asyncio
import random
import string
import aiohttp

from aiohttp import ClientSession
from pathlib import Path
from urllib.parse import urlparse, urljoin, urlunparse
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from weasyprint import HTML, CSS


# Importing local modules
from functions import AppConfig, generate_pdf, convert_url_to_pdf_task, cleanup_downloads_folder, scrape_site

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
    servers=[{"url": f"http://pdf", "description": "Base API server"}]
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

    # Wait for the file to exist (with timeout)
    await asyncio.sleep(3)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 10:
            pdf_url = f"{config.BASE_URL}/downloads/{request.output_filename}"
            return JSONResponse(status_code=202, content={"message": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

    return FileResponse(path=output_path, filename=request.output_filename, media_type='application/pdf')

# Endpoint for converting URLs to PDFs
@app.post("/convert_urls", operation_id="url_to_pdf")
async def convert_url_to_pdf(request: ConvertURLRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    url = request.url.strip()

    # Clean the URL by removing query parameters and fragments
    parsed_url = urlparse(url)
    clean_url = urlunparse(parsed_url._replace(query="", fragment=""))

    # Extract and sanitize filename from URL path
    path_segments = parsed_url.path.strip('/').split('/')
    filename_base = '-'.join(filter(None, path_segments)) or parsed_url.netloc
    filename_base = re.sub(r'[^a-zA-Z0-9\-\.]', '-', filename_base)  # Replace non-allowed characters with hyphens
    filename_base = re.sub(r'[_]+', '-', filename_base)  # Convert any underscores to hyphens
    filename_base = re.sub(r'-{2,}', '-', filename_base)  # Consolidate multiple consecutive hyphens into one

    # Check for root domain without path
    if filename_base == parsed_url.netloc:
        filename_base = parsed_url.netloc.split('.')[0]  # Use the domain name part only, without TLD

    # Remove any trailing hyphens before adding the datetime suffix
    filename_base = filename_base.rstrip('-')

    datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    output_filename = f"{filename_base}-{datetime_suffix}.pdf"
    output_path = Path("/app/downloads") / output_filename

    # Start background task to convert the URL to PDF
    background_tasks.add_task(
        convert_url_to_pdf_task,
        url=clean_url,
        output_path=output_path
    )

    # Wait for the file to exist (with timeout)
    await asyncio.sleep(3)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 10:
            pdf_url = f"{config.BASE_URL}/downloads/{output_filename}"
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
                if response.status == 200:
                    # Parse the response data to get the ID
                    response_data = await response.json()
                    kb_id = response_data.get("id", "")
                    return JSONResponse(status_code=200, content={"message": f"Knowledge Base '{request.name}' created successfully.", "id": kb_id})
                else:
                    # Handle non-200 responses
                    response_data = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"API request failed to create the KB. Details: {response_data}")

    @app.post("/kb-scraper/", operation_id="web_to_kb")
    async def scrape_to_kb(request: KBSubmissionRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
        # Add task with correct parameters
        background_tasks.add_task(scrape_site, request.website_url, request.dataset_id)
        return {"message": f"Scraping {request.website_url} to Knowledge Base {request.dataset_id} initiated. Check dataset for updates."}

# Root endpoint serving index.html directly
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("/app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
