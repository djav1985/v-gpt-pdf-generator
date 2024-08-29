# models.py
from pydantic import BaseModel, Field
from typing import Optional

# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    pdf_title: str = Field(
        ...,
        description="Title of the PDF document; will be used as <h1>$title</h1>.",
    )
    body_content: str = Field(
        ...,
        description="HTML content for the PDF body; will be used as <body>$body_content</body>. Can include element IDs, class attributes, and <img> tags with absolute URLs. Images from DALL-E via absolute URLs are also supported. Customize styling with the 'css_content' parameter.",
    )
    css_content: Optional[str] = Field(
        None,
        description="Optional CSS styles to format the 'body_content'.",
    )
    output_filename: Optional[str] = Field(
        default=None,
        description="Optional filename for the PDF, use - for spaces and do not include the extension.",
    )
