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
        
        # Validate that CSS content only contains allowed properties
        allowed_css_properties = [
            "color", "font-size", "margin", "padding", "background", "border", "width", "height", "display",
            "position", "top", "left", "right", "bottom", "overflow", "text-align", "line-height", "font-weight",
            "font-family", "border-radius", "opacity", "z-index"
        ]
        
        # Split the CSS rules by ";" and check each rule
        css_rules = value.split(";")
        for rule in css_rules:
            if not rule.strip():  # Skip empty rules
                continue
            
            property_name = rule.split(":")[0].strip().lower()  # Get the property name
            if property_name not in allowed_css_properties:  # Check against allowed properties
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
        
        # Validate that CSS content only contains allowed properties
        allowed_css_properties = [
            "color", "font-size", "margin", "padding", "background", "border", "width", "height", "display",
            "position", "top", "left", "right", "bottom", "overflow", "text-align", "line-height", "font-weight",
            "font-family", "border-radius", "opacity", "z-index"
        ]
        
        # Split the CSS rules by ";" and check each rule
        css_rules = value.split(";")
        for rule in css_rules:
            if not rule.strip():  # Skip empty rules
                continue
            
            property_name = rule.split(":")[0].strip().lower()  # Get the property name
            if property_name not in allowed_css_properties:  # Check against allowed properties
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
