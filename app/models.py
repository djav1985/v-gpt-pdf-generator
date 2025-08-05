# /models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class CreatePDFRequest(BaseModel):
    # Title of the PDF document; required field with specific length constraints and description
    pdf_title: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description=(
            "Title of the PDF document; will be used as both the <h1>$title</h1> in the body and the <title>$title</title>. "
            "Must be between 3 and 100 characters and contain only alphanumeric characters and spaces."
        ),
    )
    
    # Flag indicating if the body content contains code blocks
    contains_code: bool = Field(
        default=False,
        description=(
            "Indicates whether the 'body_content' includes code blocks. If set to true, the content may contain pre-formatted "
            "code blocks using <pre><code> tags. To include code blocks, wrap code snippets in <pre><code>...</code></pre> tags. "
            "Specify the language using a class attribute, e.g., <code class=\"language-python\">."
        ),
    )
    
    # HTML content for the body of the PDF; required field with minimum length
    body_content: str = Field(
        ..., 
        min_length=10, 
        description=(
            "HTML content for the PDF body. This will be inserted inside the <body> element of the PDF document. "
            "Use the 'pdf_title' parameter to set the <h1> heading; do not include an <h1> tag in the 'body_content'. "
            "Do not include <html>, <body>, <head>, or similar tags. "
            "You can use standard HTML tags such as <h2>, <h3>, <h4>, <p>, <div>, <span>, <ul>, <ol>, <li>, <img>, <a>, <table>, <tr>, <th>, <td>, etc., to structure your content. "
            "Must be at least 10 characters long."
        ),
    )
    
    # Optional CSS styles for formatting the body content
    css_content: Optional[str] = Field(
        default=None,
        max_length=5000,
        description=(
            "Optional CSS styles to format the 'body_content' using selectors like tags, classes, and IDs. "
            "Provide custom styles or override default styles to achieve the desired layout and design. "
            "Must not exceed 5000 characters and must only contain valid CSS characters."
        ),
    )
    
    # Optional filename for the generated PDF
    output_filename: Optional[str] = Field(
        default=None,
        max_length=100,
        description=(
            "Optional filename for the generated PDF. Use hyphens for spaces and do not include the file extension. "
            "Must only contain alphanumeric characters and hyphens, and be no longer than 100 characters."
        ),
    )

    @field_validator("body_content")
    def validate_body_content(cls, value: str):
        # Ensure no forbidden tags (e.g., <html>, <body>, <head>) are included in the body content
        forbidden_tags = ["<html", "<body", "<head", "<title", "<!doctype", "<script", "<iframe"]
        for tag in forbidden_tags:
            if re.search(f"{tag}\s*>?", value, re.IGNORECASE):
                raise ValueError(
                    f"The 'body_content' must not contain forbidden tags like {', '.join(forbidden_tags)}."
                )
        
        # Ensure no <h1> tag is included; instead, the pdf_title should be used for this
        if re.search(r"<h1\s*>", value, re.IGNORECASE):
            raise ValueError("The 'body_content' must not contain <h1> tags. Use 'pdf_title' for the main heading.")
        
        return value

    @field_validator("css_content")
    def validate_css_content(cls, value: Optional[str]):
        if value is None:
            return value

        # Reference list of supported CSS properties (as per WeasyPrint documentation)
        allowed_css_properties = [
            "align-content", "align-items", "align-self", "all", "animation", "background", "background-attachment",
            "background-blend-mode", "background-clip", "background-color", "background-image", "background-origin",
            "background-position", "background-repeat", "background-size", "border", "border-bottom", "border-bottom-color",
            "border-bottom-left-radius", "border-bottom-right-radius", "border-bottom-style", "border-bottom-width",
            "border-collapse", "border-color", "border-left", "border-left-color", "border-left-style", "border-left-width",
            "border-radius", "border-right", "border-right-color", "border-right-style", "border-right-width",
            "border-spacing", "border-style", "border-top", "border-top-color", "border-top-left-radius",
            "border-top-right-radius", "border-top-style", "border-top-width", "border-width", "bottom", "box-decoration-break",
            "box-shadow", "box-sizing", "caption-side", "clear", "clip", "color", "content", "cursor", "direction", "display",
            "empty-cells", "flex", "flex-basis", "flex-direction", "flex-flow", "flex-grow", "flex-shrink", "flex-wrap",
            "float", "font", "font-family", "font-feature-settings", "font-kerning", "font-size", "font-size-adjust",
            "font-stretch", "font-style", "font-variant", "font-variant-caps", "font-variant-ligatures", "font-variant-numeric",
            "font-weight", "height", "hyphens", "justify-content", "left", "letter-spacing", "line-height", "list-style",
            "list-style-image", "list-style-position", "list-style-type", "margin", "margin-bottom", "margin-left",
            "margin-right", "margin-top", "max-height", "max-width", "min-height", "min-width", "opacity", "order", "orphans",
            "outline", "outline-color", "outline-offset", "outline-style", "outline-width", "overflow", "overflow-wrap",
            "padding", "padding-bottom", "padding-left", "padding-right", "padding-top", "page-break-after", "page-break-before",
            "page-break-inside", "perspective", "perspective-origin", "position", "quotes", "resize", "right", "scroll-behavior",
            "tab-size", "table-layout", "text-align", "text-align-last", "text-combine-upright", "text-decoration",
            "text-decoration-color", "text-decoration-line", "text-decoration-style", "text-indent", "text-orientation",
            "text-overflow", "text-shadow", "text-transform", "top", "transform", "transform-origin", "transform-style",
            "transition", "transition-delay", "transition-duration", "transition-property", "transition-timing-function",
            "unicode-bidi", "vertical-align", "visibility", "white-space", "widows", "width", "word-break", "word-spacing",
            "word-wrap", "z-index"
        ]

        # Validate each CSS property in the provided content
        css_blocks = value.split("}")
        for block in css_blocks:
            block = block.strip()
            if not block:
                continue

            if "{" not in block:
                raise ValueError("Invalid CSS format: missing '{'.")

            selector, properties = block.split("{", 1)
            selector = selector.strip()
            properties = properties.strip()

            if not selector:
                raise ValueError("CSS selector cannot be empty.")

            css_rules = properties.split(";")
            for rule in css_rules:
                rule = rule.strip()
                if not rule:
                    continue

                if ":" not in rule:
                    raise ValueError(f"Invalid CSS rule format: '{rule}'")

                property_name, _ = rule.split(":", 1)
                property_name = property_name.strip().lower()

                # Validate property name
                if property_name not in allowed_css_properties:
                    raise ValueError(f"The 'css_content' contains an invalid CSS property: {property_name}")

        return value

    @field_validator("output_filename")
    def validate_output_filename(cls, value: Optional[str]):
        if value is None:
            return value

        # Validate that output filename meets the constraints
        if not re.match(r'^[a-zA-Z0-9\-]+$', value):  # Only allows alphanumerics and hyphens
            raise ValueError("The 'output_filename' must only contain alphanumeric characters and hyphens.")

        if len(value) < 3:  # Minimum length requirement
            raise ValueError("The 'output_filename' must be at least 3 characters long.")

        return value
