# /dependencies.py 
import os
import re
import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from weasyprint import HTML
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

# PDF generation tasks
async def generate_pdf(pdf_title: str, body_content: str, css_content: str, output_path: Path, contains_code: bool) -> None:
    try:
        # Retrieve environment variables for footer customization; set defaults if not available
        footer_name = os.getenv("FOOTER_NAME", "Vontainment.com")
        
        # Define default CSS styles for the PDF layout and appearance
        default_css = f"""
        @page {{
            size: Letter;
            margin: 0.5in;
            @bottom {{
                border-top: 2px solid #66cc33;
                padding-top: 10px;
            }}
            @bottom-left {{
                content: "© {datetime.now().year} {footer_name}";
                font-size: 10px;
                color: #66cc33;
                margin-left: 0.5in;
                margin-bottom: 0.25in;
            }}
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #66cc33;
                margin-right: 0.5in;
                margin-bottom: 0.25in;
            }}
        }}
        body {{
            font-family: 'Arial', sans-serif;
            font-size: 12px;
            line-height: 1.5;
            color: #333;
            margin-bottom: 100px; /* Ensure space for footer */
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
        }}
        """

        # Initialize combined_css with the default CSS wrapped in a <style> tag
        combined_css = f"<style>{default_css}</style>"

        # Append provided CSS content within its own <style> tag, if any
        if css_content:
            combined_css += f"<style>{css_content}</style>"

        # If the body content contains code, process it to highlight syntax
        if contains_code:
            # Use regex to find all <pre><code> blocks in the body content
            code_blocks = re.findall(r'<pre><code class="language-(\w+)">(.+?)</code></pre>', body_content, re.DOTALL)

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

# Function to clean up older files in the downloads folder
async def cleanup_downloads_folder(folder_path: str) -> None:
    try:
        now = datetime.now()  # Get the current date and time
        age_limit = now - timedelta(days=7)  # Set age limit to 7 days
        filenames = await asyncio.to_thread(os.listdir, folder_path)  # List files in the provided folder path
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)  # Construct full file path
            if await aiofiles.os.path.isfile(file_path):  # Check if it's a file
                file_mod_time = datetime.fromtimestamp(
                    await asyncio.to_thread(os.path.getmtime, file_path)  # Get the last modification time of the file
                )
                # Remove the file if it is older than the age limit
                if file_mod_time < age_limit:
                    await asyncio.to_thread(os.remove, file_path)
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
