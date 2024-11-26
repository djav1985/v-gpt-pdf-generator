# /routes/create.py
import os
import random
import string

from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from models import CreatePDFRequest
from dependencies import generate_pdf, cleanup_downloads_folder, get_api_key


pdf_router = APIRouter()

@pdf_router.post("/", operation_id="create_pdf")
async def create_pdf(
    request: CreatePDFRequest,
    api_key: str = Depends(get_api_key),
) -> JSONResponse:
    filename_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    random_chars = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    filename = (
        f"{random_chars}{filename_suffix}.pdf"
        if request.output_filename is None
        else f"{request.output_filename}{filename_suffix}.pdf"
    )
    output_path = Path("/app/downloads") / filename

    try:
        # Generate the PDF using the provided parameters, including contains_code
        await generate_pdf(
            pdf_title=request.pdf_title,
            body_content=request.body_content,
            css_content=request.css_content or '',  # Directly using request.css_content
            output_path=output_path,
            contains_code=request.contains_code  # Passing contains_code directly
        )

        return JSONResponse(content={
            "results": "PDF generation is complete. You can download it from the following URL:",
            "url": f"{os.getenv('BASE_URL')}{os.getenv('ROOT_PATH', '')}/downloads/{filename}",
        })
        
    except ValueError as e:
        print(f"Value error occurred: {e}")
        raise HTTPException(status_code=400, detail="A value error occurred while processing the PDF generation.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while generating the PDF.")
