# Importing necessary modules and libraries
from os import getenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import pdfkit
import asyncio
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

# Function to generate a PDF from provided HTML and CSS content
async def generate_pdf(html_content, css_content, output_path, options=None):
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

    # Generate the PDF using pdfkit and asyncio for non-blocking operation
    try:
        await asyncio.to_thread(pdfkit.from_string, html_content, output_path, options=default_options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for creating a new PDF
@app.post("/create")
async def create_pdf(request: CreatePDFRequest):
    # Define the output path for the generated PDF
    output_path = Path("/app/downloads") / f"{request.output_filename}.pdf"
    # Call the generate_pdf function to create the PDF
    await generate_pdf(
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )

    # If the file does not exist after generation, raise a 404 error
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Return the generated PDF as a FileResponse
    return FileResponse(path=str(output_path), filename=f"{request.output_filename}.pdf", media_type='application/pdf')
