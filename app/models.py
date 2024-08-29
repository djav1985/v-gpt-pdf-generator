# models.py
from pydantic import BaseModel, Field
from typing import Optional

# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    pdf_title: str = Field(
        ...,
        description="Title of the PDF document; will be used as both the <h1>$title</h1> in the body and the <title>$title<title>.",
    )
    html_content: str = Field(
        ...,
        description=(
            "HTML content for the PDF body. This will be inserted inside the <body> element of the PDF document. "
            "Use the 'pdf_title' parameter to set the <h1> heading; do not include an <h1> tag in the 'html_content'. "
            "You can use standard HTML tags such as <h2>, <h3>, <h4>, <p>, <div>, <span>, <ul>, <ol>, <li>, <img>, <a>, <table>, <tr>, <th>, <td>, etc to structure your content. "
            "Include classes and IDs within the HTML elements and use the 'css_content' parameter to apply custom styles. "
            "Images should use absolute URLs. "
            "Scripts and embedded forms are not supported."
        ),
    )
    css_content: Optional[str] = Field(
        default=None,
        description=(
            "Optional CSS styles to format the HTML content. Style elements using selectors like tags, classes, and IDs. "
            "Provide custom styles or override default styles to achieve desired layout and design."
        ),
    )
    output_filename: Optional[str] = Field(
        default=None,
        description="Optional filename for the generated PDF. Use hyphens for spaces and do not include the file extension.",
    )

