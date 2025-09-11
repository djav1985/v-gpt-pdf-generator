# /routes/create.py
import random
import string
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..models import CreatePDFRequest, CreatePDFResponse, ErrorResponse
from ..dependencies import generate_pdf, get_api_key
from ..config import settings


logger = logging.getLogger(__name__)

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
                        "example": {
                            "status": 403,
                            "code": "invalid_api_key",
                            "message": "Invalid or missing API key",
                            "details": "Provide a valid API key in the Authorization header",
                        }
                    }
                }
            },
            "500": {
                "content": {
                    "application/json": {
                        "example": {
                            "status": 500,
                            "code": "internal_server_error",
                            "message": "Internal Server Error",
                            "details": "An unexpected error occurred",
                        }
                    }
                }
            },
        },
    },
)
async def create_pdf(request: CreatePDFRequest) -> CreatePDFResponse:
    """Generate a PDF file from the provided request data.

    Args:
        request: Parameters for PDF generation.

    Returns:
        CreatePDFResponse: Information about the generated PDF file.

    Raises:
        HTTPException: If PDF generation fails or a filesystem error occurs.
    """
    filename_suffix = datetime.now(tz=timezone.utc).strftime("-%Y%m%d%H%M%S")
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
            css_content=request.css_content,
            output_path=output_path,
            contains_code=request.contains_code  # Passing contains_code directly
        )

        return CreatePDFResponse(
            results="PDF generation is complete. You can download it from the following URL:",
            url=f"{settings.BASE_URL}{settings.ROOT_PATH}/downloads/{filename}",
        )
    except HTTPException:
        raise
    except OSError as e:
        logger.error("File error creating PDF: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "code": "internal_server_error",
                "message": "Internal Server Error",
                "details": str(e),
            },
        ) from e
    except Exception as e:
        logger.exception("Unexpected error creating PDF")
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "code": "internal_server_error",
                "message": "Internal Server Error",
                "details": str(e),
            },
        ) from e
