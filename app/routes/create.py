# /routes/create.py
import os
import random
import string
import asyncio
import time
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, JSONResponse
from starlette.responses import FileResponse

from models import CreatePDFRequest
from functions import generate_pdf, cleanup_downloads_folder


pdf_router = APIRouter()

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
            pdf_url = f"{os.getenv("os.getenv("BASE_URL")")}/downloads/{request.output_filename}"
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
