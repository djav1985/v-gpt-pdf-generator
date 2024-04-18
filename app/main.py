# Importing necessary modules and libraries
import os
import requests
import time
import asyncio
import random
import string

from pathlib import Path
from urllib.parse import urlparse
from typing import List
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from weasyprint import HTML, CSS

# Importing local modules
from functions import load_configuration, generate_pdf, convert_url_to_pdf, cleanup_downloads_folder

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
    html_content: str = Field(..., description="HTML content that will be converted into a PDF document.")
    css_content: Optional[str] = Field(default=None, description="Optional CSS content for styling the HTML. If not provided, a default styling will be applied.")
    output_filename: Optional[str] = Field(default=None, description="Optional name for the generated PDF file. If not provided, a default name with a timestamp will be generated.")

# Request model for converting URLs to PDFs
class ConvertURLsRequest(BaseModel):
    urls: str = Field(..., description="Comma-separated list of upto 5 URLs to be converted into PDFs. Each URL should return HTML content that can be rendered into a PDF.")


# Endpoint for creating a new PDF
@app.post("/create", operation_id="create_pdf")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):

    background_tasks.add_task(cleanup_downloads_folder, "/app/downloads/")

    # Default CSS
    default_css = "body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }"

    # Use provided CSS or the default
    css_content = request.css_content if request.css_content else default_css

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
            return JSONResponse(status_code=202, content={"detail": "PDF generation is still in progress. Please check the URL after some time.", "url": pdf_url})

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
            executor.submit,
            convert_url_to_pdf,
            url=url.strip(),  # strip() to remove any leading/trailing whitespace
            output_path=output_path
        )
        files_and_paths.append((output_path, output_filename))

    # Check if all files exist or wait until timeout
    start_time = time.time()
    all_files_ready = False
    while time.time() - start_time < 15:
        if all(path.exists() for path, _ in files_and_paths):
            all_files_ready = True
            break
        await asyncio.sleep(1)

    if not all_files_ready:
        response_content = {
            "detail": "PDF generation is still in progress. Please check the URLs after some time.",
            "files": []
        }
        for _, output_filename in files_and_paths:
            pdf_url = f"{BASE_URL}/downloads/{output_filename}"
            response_content["files"].append({"filename": output_filename, "url": pdf_url})
        return JSONResponse(status_code=202, content=response_content)

    output_path, output_filename = files_and_paths[0]
    return FileResponse(path=output_path, filename=output_filename, media_type='application/pdf')

# Root endpoint serving index.html directly
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("/app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="/app/public"), name="static")
