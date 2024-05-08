# Importing required libraries and modules
import os
import asyncio
import aiofiles.os
from pathlib import Path
from datetime import datetime, timedelta
from weasyprint import HTML, CSS
from fastapi import HTTPException, Depends, HTTPBearer


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
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: HTML(string=html_content).write_pdf(
                target=output_path, stylesheets=[css]
            ),
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
