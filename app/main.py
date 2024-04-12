# Importing necessary modules and libraries
from fastapi import FastAPI, HTTPException, BackgroundTasks  # FastAPI framework components
from fastapi.responses import FileResponse  # Response class for serving files
from fastapi.staticfiles import StaticFiles  # Serve static files
from fastapi import FastAPI, HTTPException, Security, Depends, BackgroundTasks
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path  # Path manipulation
from os import getenv  # Environment variables
from pydantic import BaseModel  # Data validation
from weasyprint import HTML, CSS  # PDF generation
from urllib.parse import urlparse  # URL parsing
from typing import List  # Type hinting
from concurrent.futures import ThreadPoolExecutor  # Asynchronous execution
import requests  # HTTP requests


# Base URL for the API server
BASE_URL = getenv("BASE_URL", "http://localhost")

# Optional API key from the environment
API_KEY = getenv("API_KEY")
bearer_scheme = HTTPBearer(auto_error=False)  # Avoid auto error to handle no Authorization header gracefully

async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if API_KEY:  # Check if API_KEY is set
        if not credentials or credentials.credentials != API_KEY:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")
    # If API_KEY is not set, or if the provided credentials are valid, allow access
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

# Function to generate a PDF from provided HTML and CSS content
def generate_pdf(html_content, css_content, output_path):
    # If CSS content is provided, prepend it to the HTML content
    if css_content and css_content.strip():
        html_content = f"<style>{css_content}</style>{html_content}"

    # Generate the PDF using WeasyPrint
    try:
        HTML(string=html_content).write_pdf(output_path, stylesheets=[CSS(string=css_content)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for creating a new PDF
@app.post("/create", operation_id="create_pdf")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    # Define the output path for the generated PDF
    output_path = Path("/app/downloads") / f"{request.output_filename}"

    # Start the background task to generate the PDF
    background_tasks.add_task(
        executor.submit,
        generate_pdf,
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )

    # Return the URL where the PDF will be available
    pdf_url = f"{BASE_URL}/downloads/{request.output_filename}"
    return {"detail": "PDF generation started", "url": pdf_url}

# Request model for converting URLs to PDFs
class ConvertURLsRequest(BaseModel):
    urls: List[str]  # List of URLs to convert to PDFs

# Function to convert a URL to a PDF
def convert_url_to_pdf(url: str, output_path: str):
    """Fetch HTML from URL and convert it to a PDF file."""
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad requests
        html_content = response.text
        # Generate PDF from HTML content
        HTML(string=html_content).write_pdf(output_path)
    except Exception as e:
        print(f"Failed to convert {url} to PDF: {str(e)}")  # Log error

# Endpoint for converting URLs to PDFs
@app.post("/convert_urls", operation_id="convert_urls_to_pdfs")
async def convert_urls_to_pdfs(request: ConvertURLsRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    # Validate the number of URLs
    if len(request.urls) > 5:
        raise HTTPException(status_code=400, detail="Too many URLs provided. Please limit to 5.")

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

    # Return the URLs where the PDFs will be available
    pdf_urls = [f"{BASE_URL}/downloads/{urlparse(url).path.strip('/').split('/')[-1]}.pdf" for url in request.urls]
    return {"detail": "PDF generation started", "urls": pdf_urls}

# Root endpoint serving index.html directly
@app.get("/")
async def root():
    return FileResponse("app/public/index.html")

# Mount a static files directory at /downloads to serve generated PDFs
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="app/public"), name="static")
