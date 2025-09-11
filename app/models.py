from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


# Request model for creating a PDF
class CreatePDFRequest(BaseModel):
    pdf_title: str = Field(
        ...,
        description="Title of the PDF document; will be used as both the <h1>$title</h1> in the body and the <title>$title</title>.",
        example="Example PDF",
    )
    contains_code: bool = Field(
        default=False,
        description=(
            "Indicates whether the 'body_content' includes code blocks. If set to true, the content may contain pre-formatted "
            "code blocks using <pre><code> tags. To include code blocks, wrap snippets in <pre><code>...</code></pre> tags and "
            "specify the language using a class attribute, e.g., <code class=\"language-python\"></code>."
        ),
        example=True,
    )
    body_content: str = Field(
        ...,
        description=(
            "HTML content for the PDF body. This will be inserted inside the <body> element of the PDF document. "
            "Use the 'pdf_title' parameter to set the <h1> heading; do not include an <h1> tag in the 'body_content'. "
            "You can use standard HTML tags such as <h2>, <h3>, <h4>, <p>, <div>, <span>, <ul>, <ol>, <li>, <img>, <a>, <table>, <tr>, <th>, <td>, etc., to structure your content. "
            "Include classes and IDs within the HTML elements and use the 'css_content' parameter to apply custom styles. "
            "Images should use absolute URLs. "
            "Scripts and embedded forms are not supported."
        ),
        example="<p>Hello World</p>",
    )
    css_content: Optional[str] = Field(
        default=None,
        description=(
            "Optional CSS styles to format the 'body_content' using selectors like tags, classes, and IDs. "
            "Provide custom styles or override default styles to achieve the desired layout and design."
        ),
        example="p { color: blue; }",
    )
    output_filename: Optional[str] = Field(
        default=None,
        description="Optional filename for the generated PDF. Use hyphens for spaces and do not include the file extension.",
        example="example-pdf",
    )


# Response model for PDF creation
class CreatePDFResponse(BaseModel):
    results: str
    url: HttpUrl
