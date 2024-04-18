# Importing necessary modules and libraries
import os
import requests
import time
import asyncio
import random
import string
import aiohttp

from pathlib import Path
from urllib.parse import urlparse
from typing import List
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from weasyprint import HTML, CSS

# Importing local modules
from functions import load_configuration, generate_pdf, convert_url_to_pdf, cleanup_downloads_folder, should_skip_url, scrape_site, submit_to_kb_api

# Load configuration on startup
BASE_URL, API_KEY, KB_BASE_URL, KB_API_KEY = load_configuration()

# Setup the bearer token authentication scheme
bearer_scheme = HTTPBearer(auto_error=False)

async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if API_KEY and (not credentials or credentials.credentials != API_KEY):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return credentials.credentials if credentials else None

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    servers=[{"url": BASE_URL, "description": "Base API server"}]
)

# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    html_content: str = Field(..., description="HTML content that will be converted into a PDF document.")
    css_content: Optional[str] = Field(default="body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }", description="Optional CSS content for styling the HTML.")

# Request model for converting URLs to PDFs
class ConvertURLsRequest(BaseModel):
    urls: str = Field(..., description="Comma-separated list of upto 5 URLs to be converted into PDFs. Each URL should return HTML content that can be rendered into a PDF.")

class KBCreationRequest(BaseModel):
    """Model for creating a Knowledge Base."""
    name: str = Field(..., description="Name of the knowledge base to be created.")

class KBSubmissionRequest(BaseModel):
    """Model for submitting a document."""
    website_url: str = Field(..., description="URL of the website to scrape.")
    dataset_id: str = Field(..., description="ID of the dataset to submit the document to.")
    indexing_technique: Optional[str] = Field("high_quality", description="Indexing technique to be used.")

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
        request.output_filename = f"{random_chars}{datetime_suffix}.pdf"
    else:
        # Append datetime to provided filename
        datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
        request.output_filename += f"{datetime_suffix}.pdf"

    output_path = Path("/app/downloads") / request.output_filename
    # Start the background task to generate the PDF
    background_tasks.add_task(generate_pdf, html_content=request.html_content, css_content=css_content, output_path=output_path)

    # Wait for the file to exist (with timeout)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 15:
            pdf_url = f"{BASE_URL}/downloads/{request.output_filename}"
            return JSONResponse(status_code=202, content={"message": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

    return FileResponse(path=output_path, filename=request.output_filename, media_type='application/pdf')

# Endpoint for converting URLs to PDFs
@app.post("/convert_urls", operation_id="convert_urls_to_pdfs")
async def convert_urls_to_pdfs(request: ConvertURLsRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):

    background_tasks.add_task(cleanup_downloads_folder, "/app/downloads/")

    # Split the string of URLs into a list
    url_list = request.urls.split(',')

    # Validate the number of URLs
    if len(url_list) > 5:
        raise HTTPException(status_code=400, detail="Too many URLs provided. Please limit to 5.")

    datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    files_and_paths = []
    # Start background tasks to convert the URLs to PDFs
    for url in url_list:
        url_path = urlparse(url.strip()).path  # strip() removes any leading/trailing whitespace
        base_filename = f"{url_path.strip('/').split('/')[-1]}"
        output_filename = f"{base_filename}{datetime_suffix}.pdf"
        output_path = Path("/app/downloads") / output_filename
        background_tasks.add_task(
            convert_url_to_pdf,
            url=url.strip(),  # strip() to remove any leading/trailing whitespace
            output_path=output_path
        )
        files_and_paths.append((output_path, output_filename))

    response_content = {
        "message": "PDF generation started. Please check the URLs after some time.",
        "files": [{"filename": filename, "url": f"{BASE_URL}/downloads/{filename}"} for _, filename in files_and_paths]
    }
    return JSONResponse(status_code=202, content=response_content)

@app.post("/create-kb/", operation_id="create_new_kb")
async def create_new_kb(request: KBCreationRequest, api_key: str = Depends(get_api_key)):
    """Create an empty Knowledge Base with the provided name."""
    api_url = f"{KB_BASE_URL}/v1/datasets"
    headers = {
        "Authorization": f"Bearer {KB_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"name": request.name}

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="API request failed to create the KB.")
    return JSONResponse(status_code=200, content={"message": f"Knowledge Base {request.name} created successfully."})

@app.post("/kb-scraper/", operation_id="scrape_to_kb")
async def scrape_to_kb(request: KBSubmissionRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        async for url, text in scrape_site(request.website_url, session):
            background_tasks.add_task(submit_to_kb_api, url, text, request.dataset_id, request.indexing_technique, session)

    return JSONResponse(status_code=200, content={"message": f"Scraping {request.website_url} to Knowledge Base {request.dataset_id} initiated. Check dataset for updates."})

# Root endpoint serving index.html directly
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("/app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
