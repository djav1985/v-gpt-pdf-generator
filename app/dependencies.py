# /dependencies.py 
import os
import re
import asyncio

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from weasyprint import HTML
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer


FOOTER_NAME = os.getenv("FOOTER_NAME", "Vontainment.com")

DEFAULT_PDF_CSS = f"""
@page {{
    size: Letter;
    margin: 0.25in 0.5in 0.5in 0.5in;
    @bottom-left {{
        content: \"© {datetime.now().year} {FOOTER_NAME}\";
        font-size: 10px;
        color: #66cc33;
        margin-bottom: 0.25in;
    }}
    @bottom-right {{
        content: \"Page \" counter(page) \" of \" counter(pages);
        font-size: 10px;
        color: #66cc33;
        margin-bottom: 0.25in;
    }}
}}
body {{
    font-family: 'Arial', sans-serif;
    font-size: 12px;
    line-height: 1.5;
    color: #333;
}}
h1 {{
    color: #66cc33;
    margin-bottom: 20px;
    border-bottom: 1px solid #66cc33;
    padding-bottom: 10px;
}}
h2, h3, h4, h5, h6 {{
    color: #4b5161;
    margin-bottom: 20px;
    page-break-after: avoid;
    page-break-inside: avoid;
}}
p, table, ul, ol, pre, code, blockquote, img, li, thead, tbody, tr {{
    page-break-inside: avoid;
    orphans: 3;
    widows: 3;
}}
p {{
    margin: 1em 0;
}}
a {{
    color: #0366d6;
    text-decoration: none;
}}
a:hover {{
    text-decoration: underline;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: #f4f4f4;
    font-weight: bold;
}}
pre, code {{
    padding: 10px;
    border: 1px solid #ccc;
    background-color: #f4f4f4;
    page-break-inside: avoid;
}}
"""

CODE_BLOCK_RE = re.compile(r'<pre><code class="language-(\\w+)">(.+?)</code></pre>', re.DOTALL)

# PDF generation tasks
async def generate_pdf(pdf_title: str, body_content: str, css_content: str, output_path: Path, contains_code: bool) -> None:
    try:
        # Initialize combined_css with the default CSS wrapped in a <style> tag
        combined_css = f"<style>{DEFAULT_PDF_CSS}</style>"

        # Append provided CSS content within its own <style> tag, if any
        if css_content:
            combined_css += f"<style>{css_content}</style>"

        # If the body content contains code, process it to highlight syntax
        if contains_code:
            # Use precompiled regex to find all <pre><code> blocks in the body content
            code_blocks = CODE_BLOCK_RE.findall(body_content)

            # Prepare Pygments formatter and extract CSS for syntax highlighting
            formatter = HtmlFormatter(style='default')
            pygments_css = formatter.get_style_defs('.highlight')
            combined_css += f"<style>{pygments_css}</style>"

            # Highlight each code block found in the body content
            for idx, (language, code) in enumerate(code_blocks):
                try:
                    lexer = get_lexer_by_name(language)  # Get the appropriate lexer
                except Exception:
                    lexer = guess_lexer(code)  # Fallback to guessing the lexer if the language is unknown
                # Highlight the code block and replace the original code block with highlighted HTML
                highlighted_code = highlight(code, lexer, formatter)
                body_content = body_content.replace(f'<pre><code class="language-{language}">{code}</code></pre>', f'<div id="code-block-{idx}">{highlighted_code}</div>')

        # Construct the final HTML template for the PDF
        html_template = f"""
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

        # Asynchronously generate the PDF from the constructed HTML string
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: HTML(string=html_template).write_pdf(target=str(output_path))  # Write the PDF to the specified output path
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")  # Raise HTTP exception for the error

def _cleanup_downloads_sync(folder_path: str) -> None:
    now = datetime.now()
    age_limit = now - timedelta(days=7)
    for path in Path(folder_path).iterdir():
        if path.is_file() and datetime.fromtimestamp(path.stat().st_mtime) < age_limit:
            path.unlink()


# Function to clean up older files in the downloads folder
async def cleanup_downloads_folder(folder_path: str) -> None:
    try:
        await asyncio.to_thread(_cleanup_downloads_sync, folder_path)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")  # Log the cleanup error
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")  # Raise HTTP exception for the cleanup error

async def get_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[str]:
    # Retrieve the API key from the environment
    expected_key = os.getenv("API_KEY")

    # If API_KEY is set in the environment, enforce validation
    if expected_key:
        if not credentials or credentials.credentials != expected_key:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")

    # If API_KEY is not set, allow access without validation
    return credentials.credentials if credentials else None
