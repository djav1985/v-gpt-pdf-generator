# Importing required libraries and modules
import os
import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta

from weasyprint import HTML, CSS
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

import re

# PDF generation tasks
async def generate_pdf(pdf_title: str, body_content: str, css_content: str, output_path: Path, contains_code: bool):
    try:
        # Define default CSS as a string using an f-string for formatting
        default_css = f"""
        @page {{
            size: Letter;
            margin: 0.5in;  /* Use a margin for content and space for the footer */
            @bottom-left {{
                content: "{pdf_title}";
                font-size: 10px;
                color: #555;
            }}
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #555;
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
            margin-bottom: 40px; /* 40px space below h1 */
            border-bottom: 2px solid #66cc33; /* Line under heading for separation */
            padding-bottom: 10px; /* Space below the line */
        }}
        h2, h3, h4, h5, h6 {{
            color: #4b5161;
            margin-top: 20px;  /* Add space above subheadings */
        }}
        p {{
            margin: 1em 0;  /* Consistent paragraph spacing */
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;  /* Indicate clickable links */
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;  /* Space below tables */
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
        """

        # Initialize combined_css with the default CSS in its own <style> tag
        combined_css = f"<style>{default_css}</style>"

        # Append provided CSS content if any, within its own <style> tag
        if css_content:
            combined_css += f"<style>{css_content}</style>"

        # Process body_content with Pygments if contains_code is True
        if contains_code:
            # Use regex to find all <pre><code> blocks
            code_blocks = re.findall(r'<pre><code class="language-(\w+)">(.+?)</code></pre>', body_content, re.DOTALL)

            formatter = HtmlFormatter(style='default')
            pygments_css = formatter.get_style_defs('.highlight')
            combined_css += f"<style>{pygments_css}</style>"

            for language, code in code_blocks:
                try:
                    lexer = get_lexer_by_name(language)
                except Exception:
                    lexer = guess_lexer(code)  # Fallback to guess if the language is not recognized

                # Highlight the code block
                highlighted_code = highlight(code, lexer, formatter)

                # Replace original code block with highlighted HTML
                body_content = body_content.replace(f'<pre><code class="language-{language}">{code}</code></pre>', highlighted_code)

        # Initialize the HTML template with combined_css
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

        # Asynchronously generate the PDF from the HTML string
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: HTML(string=html_template).write_pdf(target=output_path)
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Function to clean up the downloads folder
async def cleanup_downloads_folder(folder_path: str):
    try:
        now = datetime.now()
        age_limit = now - timedelta(days=7)
        filenames = await asyncio.to_thread(os.listdir, folder_path)
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            if await aiofiles.os.path.isfile(file_path):
                file_mod_time = datetime.fromtimestamp(
                    await asyncio.to_thread(os.path.getmtime, file_path)
                )
                if file_mod_time < age_limit:
                    await asyncio.to_thread(os.remove, file_path)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")

# This function checks if the provided API key is valid or not
async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    if os.getenv("API_KEY") and (
        not credentials or credentials.credentials != os.getenv("API_KEY")
    ):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return credentials.credentials if credentials else None