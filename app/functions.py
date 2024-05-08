# Importing required libraries and modules
import os
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta
from weasyprint import HTML, CSS
from fastapi import HTTPException


# PDF generation tasks
async def generate_pdf(html_content: str, css_content: str, output_path: Path):
    try:
        css = (
            CSS(string=css_content)
            if css_content
            else CSS(
                string="body { font-family: 'Arial', sans-serif; } h1 { color: #66cc33; } h2, h3, h4, h5, h6 { color: #4b5161; } p { margin: 0.5em 0; } a { color: #0366d6; text-decoration: none; }"
            )
        )
        HTML(string=html_content).write_pdf(target=output_path, stylesheets=[css])
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# Function to clean up the downloads folder
def cleanup_downloads_folder(folder_path: str):
    try:
        now = datetime.now()
        age_limit = now - timedelta(days=7)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if (
                os.path.isfile(file_path)
                and datetime.fromtimestamp(os.path.getmtime(file_path)) < age_limit
            ):
                os.remove(file_path)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")
