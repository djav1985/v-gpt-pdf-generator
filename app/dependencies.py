# Importing required libraries and modules
import os
import asyncio
import re

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from weasyprint import HTML
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer


async def generate_pdf(
    pdf_title: str,
    body_content: str,
    css_content: Optional[str],
    output_path: Path,
    contains_code: bool,
) -> None:
    """
    Generate a PDF file from HTML and CSS content.

    Args:
        pdf_title (str): Title of the PDF document.
        body_content (str): HTML content for the PDF body.
        css_content (Optional[str]): Optional CSS styles for the PDF.
        output_path (Path): Path to save the generated PDF file.
        contains_code (bool): Whether the body_content contains code blocks to highlight.

    Raises:
        HTTPException: If PDF generation fails.
    """
    try:
        # Define default CSS as a string using an f-string for formatting (minified version)
        default_css: str = f"""
        @page{{size:Letter;margin:0.5in;@bottom-left{{content:"{pdf_title}";font-size:10px;color:#555;}}@bottom-right{{content:"Page " counter(page) " of " counter(pages);font-size:10px;color:#555;}}}}
        body{{font-family:'Arial',sans-serif;font-size:12px;line-height:1.5;color:#333;}}
        h1{{color:#66cc33;margin-bottom:40px;border-bottom:2px solid #66cc33;padding-bottom:10px;}}
        h2,h3,h4,h5,h6{{color:#4b5161;margin-top:20px;}}
        p{{margin:1em 0;}}
        a{{color:#0366d6;text-decoration:none;}}
        a:hover{{text-decoration:underline;}}
        table{{width:100%;border-collapse:collapse;margin-bottom:20px;}}
        th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}
        th{{background-color:#f4f4f4;font-weight:bold;}}
        pre,code{{padding:20px;border:1px solid #ccc;background-color:#f4f4f4;}}
        """

        # Initialize combined_css with the default CSS in its own <style> tag
        combined_css: str = f"<style>{default_css}</style>"

        # Append provided CSS content if any, within its own <style> tag
        if css_content:
            combined_css += f"<style>{css_content}</style>"

        # Process body_content with Pygments if contains_code is True
        if contains_code:
            # Use regex to find all <pre><code> blocks, case-insensitively
            pattern = re.compile(
                r'<pre\s*>\s*<code\s+class="language-(\w+)"\s*>(.+?)</code\s*>\s*</pre\s*>',
                re.DOTALL | re.IGNORECASE,
            )

            formatter: HtmlFormatter = HtmlFormatter(style="default")
            pygments_css: str = formatter.get_style_defs(".highlight")
            combined_css += f"<style>{pygments_css}</style>"

            def repl(match: re.Match) -> str:
                language = match.group(1)
                code = match.group(2)
                try:
                    lexer = get_lexer_by_name(language)
                except Exception:
                    lexer = guess_lexer(code)  # Fallback if the language is not recognized
                return highlight(code, lexer, formatter)

            body_content = pattern.sub(repl, body_content)

        # Initialize the HTML template with combined_css
        html_template: str = f"""
        <html>
            <head>
                <title>{pdf_title}</title>
                {combined_css}
            </head>
            <body>
                <h1>{pdf_title}</h1>
                {body_content}
            </body>
        </html>
        """

        # Asynchronously generate the PDF from the HTML string
        await asyncio.to_thread(
            HTML(string=html_template).write_pdf, target=output_path
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "code": "pdf_generation_error",
                "message": "Error generating PDF",
                "details": str(e),
            },
        )


def _cleanup_folder(folder_path: str) -> None:
    """Remove files older than 7 days from the downloads folder."""
    now: datetime = datetime.now()
    age_limit: datetime = now - timedelta(days=7)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_mod_time: datetime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < age_limit:
                os.remove(file_path)


async def cleanup_downloads_folder(folder_path: str) -> None:
    """
    Remove files older than 7 days from the specified downloads folder.

    Args:
        folder_path (str): Path to the downloads folder to clean up.

    Raises:
        HTTPException: If cleanup fails.
    """
    try:
        await asyncio.to_thread(_cleanup_folder, folder_path)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "code": "cleanup_error",
                "message": "Cleanup error",
                "details": str(e),
            },
        )


def get_api_key(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> str:
    """
    Validate the provided API key from the Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP credentials from the request header.

    Returns:
        str: The API key if valid.

    Raises:
        HTTPException: If the API key is missing or invalid.
    """
    if settings.API_KEY and credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail={
                "status": 403,
                "code": "invalid_api_key",
                "message": "Invalid or missing API key",
                "details": "Provide a valid API key in the Authorization header",
            },
        )
    return credentials.credentials
