# /routes/create.py
import re
import random
import string
import asyncio
import time

from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, JSONResponse, HTTPException
from starlette.responses import FileResponse
from pathlib import Path  # Corrected import for Path
from urllib.parse import urlparse, urlunparse


from config import (
    get_api_key,
)  # Assuming 'config' is a module with a function named 'get_api_key'
from models import CreatePDFRequest, ConvertURLRequest  # Duplicate import removed

# Importing local modules
from functions import (
    AppConfig,
    generate_pdf,
    convert_url_to_pdf_task,
    cleanup_downloads_folder,
)

pdf_router = APIRouter()

# Load configuration on startup
config = AppConfig()


# Endpoint for creating a new PDF
@pdf_router.post("/create", operation_id="create_pdf")
async def create_pdf(
    request: CreatePDFRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):

    background_tasks.add_task(cleanup_downloads_folder, "/app/downloads/")

    # Use provided CSS or the default
    css_content = request.css_content

    if request.output_filename is None:
        # Generate a filename with random characters and datetime
        random_chars = "".join(
            random.choices(string.ascii_letters + string.digits, k=6)
        )
        datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
        request.output_filename = f"{random_chars}-{datetime_suffix}.pdf"
    else:
        # Append datetime to provided filename
        datetime_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
        request.output_filename += f"-{datetime_suffix}.pdf"

    output_path = Path("/app/downloads") / request.output_filename
    # Start the background task to generate the PDF
    background_tasks.add_task(
        generate_pdf,
        html_content=request.html_content,
        css_content=css_content,
        output_path=output_path,
    )

    # Wait for the file to exist (with timeout)
    await asyncio.sleep(3)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 10:
            pdf_url = f"{config.BASE_URL}/downloads/{request.output_filename}"
            return JSONResponse(
                status_code=202,
                content={
                    "message": "PDF generation is still in progress. Please check the URL after some time.",
                    "url": pdf_url,
                },
            )

    return FileResponse(
        path=output_path, filename=request.output_filename, media_type="application/pdf"
    )


# Endpoint for converting URLs to PDFs
@pdf_router.post("/convert_urls", operation_id="url_to_pdf")
async def convert_url_to_pdf(
    request: ConvertURLRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    url = request.url.strip()

    # Clean the URL by removing query parameters and fragments
    parsed_url = urlparse(url)
    clean_url = urlunparse(parsed_url._replace(query="", fragment=""))

    # Extract and sanitize filename from URL path
    path_segments = parsed_url.path.strip("/").split("/")
    filename_base = "-".join(filter(None, path_segments)) or parsed_url.netloc
    filename_base = re.sub(
        r"[^a-zA-Z0-9\-.]", "", filename_base
    )  # Remove all non-allowed characters except hyphens and periods
    filename_base = re.sub(
        r"[_]+", "-", filename_base
    )  # Convert any underscores to hyphens
    filename_base = re.sub(
        r"-{2,}", "-", filename_base
    )  # Consolidate multiple consecutive hyphens into one

    # Check for root domain without path
    if filename_base == parsed_url.netloc:
        filename_base = parsed_url.netloc.split(".")[
            0
        ]  # Use the domain name part only, without TLD

    datetime_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{filename_base}-{datetime_suffix}.pdf"
    output_path = Path("/app/downloads") / output_filename

    # Start background task to convert the URL to PDF
    background_tasks.add_task(
        convert_url_to_pdf_task, url=clean_url, output_path=output_path
    )

    # Wait for the file to exist (with timeout)
    await asyncio.sleep(3)
    start_time = time.time()
    while not output_path.exists():
        await asyncio.sleep(1)
        if time.time() - start_time > 10:
            pdf_url = f"{config.BASE_URL}/downloads/{output_filename}"
            return JSONResponse(
                status_code=202,
                content={
                    "message": "PDF generation is still in progress. Please check the URL after some time.",
                    "url": pdf_url,
                },
            )

    return FileResponse(
        path=output_path, filename=output_filename, media_type="application/pdf"
    )
