import re
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, validator


# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    pdf_title: str = Field(
        ...,
        description=(
            "Title of the PDF document; will be used as both the "
            "<h1>$title</h1> in the body and the <title>$title</title>."
        ),
        min_length=1,
        max_length=200
    )
    contains_code: bool = Field(
        False,
        description=(
            "Indicates whether the 'body_content' includes code blocks. "
            "If set to true, the content may contain pre-formatted code blocks "
            "using <pre><code> tags. To include code blocks, wrap snippets in "
            "<pre><code>...</code></pre> tags and specify the language using a "
            "class attribute, e.g., <code class=\"language-python\"></code>."
        )
    )
    body_content: str = Field(
        ...,
        description=(
            "HTML content for the PDF body. This will be inserted inside the "
            "<body> element of the PDF document. Use the 'pdf_title' parameter "
            "to set the <h1> heading; do not include an <h1> tag in the "
            "'body_content'. You can use standard HTML tags such as <h2>, <h3>, "
            "<h4>, <p>, <div>, <span>, <ul>, <ol>, <li>, <img>, <a>, <table>, "
            "<tr>, <th>, <td>, etc., to structure your content. Include classes "
            "and IDs within the HTML elements and use the 'css_content' "
            "parameter to apply custom styles. Images should use absolute URLs. "
            "Scripts and embedded forms are not supported."
        )
    )
    css_content: Optional[str] = Field(
        None,
        description=(
            "Optional CSS styles to format the 'body_content'. Supports "
            "standard selectors and properties but disallows '@import', "
            "'url()' functions, and '<script>' tags."
        )
    )
    output_filename: Optional[str] = Field(
        None,
        description=(
            "Optional filename for the generated PDF. Use lowercase letters, "
            "numbers, hyphens, or underscores. Path separators are not allowed "
            "and the '.pdf' extension is appended automatically."
        )
    )

    @validator("pdf_title", pre=True)
    def strip_title(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value

    @validator("body_content")
    def validate_body(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("body_content cannot be empty")
        prohibited = [r"<\s*h1\b", r"<\s*script\b", r"<\s*form\b"]
        for pattern in prohibited:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("body_content contains prohibited tags")
        return value

    @validator("css_content")
    def validate_css(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        lowered = value.lower()
        if any(term in lowered for term in ["@import", "url(", "<script"]):
            raise ValueError("css_content contains disallowed constructs")
        return value

    @validator("output_filename", pre=True)
    def sanitize_filename(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip().lower()
        if "/" in value or "\\" in value:
            raise ValueError("output_filename cannot contain path separators")
        if value.endswith(".pdf"):
            value = value[:-4]
        if not value:
            raise ValueError("output_filename cannot be empty")
        if len(value) > 100:
            raise ValueError("output_filename is too long")
        if not re.fullmatch(r"[a-z0-9_-]+", value):
            raise ValueError("output_filename contains invalid characters")
        return f"{value}.pdf"


# Response model for errors
class ErrorResponse(BaseModel):
    status: int = Field(
        ...,
        description="HTTP status code of the error"
    )
    code: str = Field(
        ...,
        description="Application-specific error identifier"
    )
    message: str = Field(
        ...,
        description="Human-readable summary of the error"
    )
    details: Optional[str] = Field(
        None,
        description="Additional information that may help resolve the error"
    )


# Response model for PDF creation
class CreatePDFResponse(BaseModel):
    results: str = Field(
        ...,
        description="Outcome message for the PDF generation request"
    )
    url: HttpUrl = Field(
        ...,
        description="URL where the generated PDF can be downloaded"
    )

    class Config:
        schema_extra = {
            "example": {
                "results": "PDF generation is complete. You can download it from the following URL:",
                "url": "https://example.com/downloads/example-pdf.pdf"
            }
        }
