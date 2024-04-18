# Importing necessary modules and libraries
import os
import requests
import time
import asyncio
from pathlib import Path
from urllib.parse import urlparse
from typing import List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from weasyprint import HTML, CSS

# Importing local modules
from functions import load_configuration, generate_pdf, convert_url_to_pdf


# Importing local modules
from functions import load_configuration, generate_pdf, convert_url_to_pdf

# Load configuration on startup
BASE_URL, API_KEY = load_configuration()

# Setup the bearer token authentication scheme
bearer_scheme = HTTPBearer(auto_error=False)

async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    # If the API key is not provided or does not match the expected value, return a 403 error
    if API_KEY and (not credentials or credentials.credentials != API_KEY):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing API key")

    # Return the provided API key, or None if it was not provided
    return credentials.credentials if credentials else None

# FastAPI application instance
app = FastAPI(
    title="PDF Generation API",  # API title
    version="0.1.0",  # API version
    description="A FastAPI application that generates PDFs from HTML and CSS content",  # API description
    servers=[{"url": BASE_URL, "description": "Base API server"}]  # Server information
)

# Initialize a thread pool executor for concurrent execution
executor = ThreadPoolExecutor(max_workers=5)

# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    html_content: str  # HTML content for the PDF
    css_content: str  # CSS content for styling the PDF
    output_filename: str  # Filename for the generated PDF

# Request model for converting URLs to PDFs
class ConvertURLsRequest(BaseModel):
    urls: List[str]  # List of URLs to convert to PDFs

# Endpoint for creating a new PDF
@app.post("/create", operation_id="create_pdf")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    output_path = Path("/app/downloads") / f"{request.output_filename}"

    # Start the background task to generate the PDF
    background_tasks.add_task(
        generate_pdf,
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )

    start_time = time.time()  # Record the start time for timeout tracking
    # Wait for the file to exist
    while not output_path.exists():
        await asyncio.sleep(1)  # Pause for a second and check again
        if time.time() - start_time > 30:  # Timeout after 30 seconds
            # Construct the URL where the PDF will eventually be available
            pdf_url = f"{BASE_URL}/downloads/{request.output_filename}"
            # Return a JSON response indicating the process has started and providing the download URL
            return JSONResponse(status_code=202, content={"detail": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

    # If the file is ready within the timeout, return it
    return FileResponse(path=output_path, filename=request.output_filename, media_type='application/pdf')

# Endpoint for converting URLs to PDFs
@app.post("/convert_urls", operation_id="convert_urls_to_pdfs")
async def convert_urls_to_pdfs(request: ConvertURLsRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    # Validate the number of URLs
    if len(request.urls) > 5:
        raise HTTPException(status_code=400, detail="Too many URLs provided. Please limit to 5.")

    files_and_paths = []
    # Start background tasks to convert the URLs to PDFs
    for url in request.urls:
        url_path = urlparse(url).path
        output_filename = f"{url_path.strip('/').split('/')[-1]}.pdf"
        output_path = Path("/app/downloads") / output_filename
        background_tasks.add_task(
            executor.submit,
            convert_url_to_pdf,
            url=url,
            output_path=output_path
        )
        files_and_paths.append((output_path, output_filename))

    # Check if all files exist or wait until timeout
    start_time = time.time()
    all_files_ready = False
    while time.time() - start_time < 30:  # Timeout after 30 seconds
        if all(path.exists() for path, _ in files_and_paths):
            all_files_ready = True
            break
        await asyncio.sleep(1)

    if not all_files_ready:
        # Not all files are ready, return URLs for each file
        response_content = {
            "detail": "PDF generation is still in progress. Please check the URLs after some time.",
            "files": []
        }
        for _, output_filename in files_and_paths:
            pdf_url = f"{BASE_URL}/downloads/{output_filename}"
            response_content["files"].append({"filename": output_filename, "url": pdf_url})
        return JSONResponse(status_code=202, content=response_content)

    # If all files are ready, return them (for simplicity, assuming only one PDF return is intended)
    # In practice, you might want to modify this to handle multiple file responses appropriately
    # For example, returning a ZIP of all PDFs or a list of download links
    output_path, output_filename = files_and_paths[0]  # Simplified for the first file only
    return FileResponse(path=output_path, filename=output_filename, media_type='application/pdf')

# Root endpoint serving index.html directly
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("/app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
