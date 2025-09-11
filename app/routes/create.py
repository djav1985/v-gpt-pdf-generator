# /routes/create.py
import os
import random
import string
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..models import CreatePDFRequest, CreatePDFResponse, ErrorResponse
from ..dependencies import generate_pdf, get_api_key

pdf_router = APIRouter()


@pdf_router.post(
    "/",
    operation_id="create_pdf",
    summary="Create PDF",
    description="Generate a PDF file from HTML and CSS content.",
    tags=["PDF"],
    response_model=CreatePDFResponse,
    responses={
        403: {"description": "Invalid or missing API key", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    },
    dependencies=[Depends(get_api_key)],
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "pdf_title": "Example PDF",
                        "contains_code": True,
                        "body_content": "<p>Hello World</p>",
                        "css_content": "p { color: blue; }",
                        "output_filename": "example-pdf",
                    }
                }
            }
        },
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "example": {
                            "results": (
                                "PDF generation is complete. You can download it from the "
                                "following URL:"
                            ),
                            "url": "https://example.com/downloads/example-pdf.pdf",
                        }
                    }
                }
            },
            "403": {
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid or missing API key"}
                    }
                }
            },
            "500": {
                "content": {
                    "application/json": {
                        "example": {"detail": "Internal Server Error"}
                    }
                }
            },
        },
    },
)
async def create_pdf(request: CreatePDFRequest):
    filename_suffix = datetime.now().strftime("-%Y%m%d%H%M%S")
    random_chars = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    filename = (
        f"{random_chars}{filename_suffix}.pdf"
        if request.output_filename is None
        else f"{request.output_filename[:-4]}{filename_suffix}.pdf"
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

        return {
            "results": "PDF generation is complete. You can download it from the following URL:",
            "url": f"{os.getenv('BASE_URL')}{os.getenv('ROOT_PATH', '')}/downloads/{filename}",
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
