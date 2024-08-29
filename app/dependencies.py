# Importing required libraries and modules
import os
import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta

from weasyprint import HTML, CSS

from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# PDF generation tasks
async def generate_pdf(pdf_title: str, body_content: str, css_content: str, output_path: Path):
    try:
        # Base HTML template with placeholders for title, CSS, and content
        html_template = f"""
        <html>
            <head>
                <title>{pdf_title}</title>
                <style>
                    @page {{
                        size: Letter;
                        margin: 0;
                        @bottom-center {{
                            content: "{pdf_title} - Page " counter(page) " of " counter(pages);
                            font-size: 10px;
                            color: #555;  /* Lighter footer text */
                            padding-bottom: 0.2in;
                        }}
                    }}
                    body {{
                        font-family: 'Arial', sans-serif;
                        font-size: 12px;
                        line-height: 1.5;
                        padding: 0.5in 0.5in 0.25in 0.5in;
                        margin: 0;
                        color: #333;  /* Darker text color for readability */
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
                </style>
                {f'<style>{css_content}</style>' if css_content else ''}
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