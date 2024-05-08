# /routes/create.py
import os
import random
import string
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from models import CreatePDFRequest
from functions import generate_pdf, cleanup_downloads_folder, get_api_key


pdf_router = APIRouter()


@pdf_router.post("/create", operation_id="create_pdf")
async def create_pdf(
    request: CreatePDFRequest,
    api_key: str = Depends(get_api_key),
):
    css_content = (
        request.css_content
        or "body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }"
    )
    filename_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    random_chars = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    filename = (
        f"{random_chars}{filename_suffix}.pdf"
        if request.output_filename is None
        else f"{request.output_filename}{filename_suffix}.pdf"
    )
    output_path = Path("/app/downloads") / filename

    try:
        await generate_pdf(
            html_content=request.html_content,
            css_content=css_content,
            output_path=output_path,
        )
        return {
            "results": "PDF generation is still in progress. Please check the URL after some time.",
            "url": f"{os.getenv('BASE_URL')}/downloads/{filename}",
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
