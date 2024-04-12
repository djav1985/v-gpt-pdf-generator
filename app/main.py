# Importing necessary modules and libraries
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import pdfkit
from os import getenv
from pydantic import BaseModel

# Define your request model
class CreatePDFRequest(BaseModel):
    html_content: str
    css_content: str
    output_filename: str

# Getting the base URL from environment variables. If not set, default to "http://localhost"
BASE_URL = getenv("BASE_URL", "http://localhost")

# Initialize the FastAPI app
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="A FastAPI application that generates PDFs from HTML and CSS content",
    servers=[{"url": BASE_URL, "description": "Base API server"}]
)

# Initialize a thread pool executor
executor = ThreadPoolExecutor(max_workers=5)

# Function to generate a PDF from provided HTML and CSS content
def generate_pdf(html_content, css_content, output_path, options=None):
    # Default PDF generation options
    default_options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'custom-header': [('Accept-Encoding', 'gzip')],
        'no-outline': None
    }
    # If custom options are provided, update the defaults with these
    if options:
        default_options.update(options)

    # If CSS content is provided, prepend it to the HTML content
    if css_content and css_content.strip():
        html_content = f"<style>{css_content}</style>{html_content}"

    # Generate the PDF using pdfkit
    try:
        pdfkit.from_string(html_content, output_path, options=default_options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for creating a new PDF
@app.post("/create")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks):
    # Define the output path for the generated PDF
    output_path = Path("/app/downloads") / f"{request.output_filename}.pdf"

    # Start the background task to generate the PDF
    background_tasks.add_task(
        executor.submit,
        generate_pdf,
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )

    # Return the URL where the PDF will be available
    pdf_url = f"{BASE_URL}/downloads/{request.output_filename}.pdf"
    return {"detail": "PDF generation started", "url": pdf_url}

# Mount a static files directory at /downloads
app.mount("/downloads", StaticFiles(directory="/app/downloads"), name="downloads")
