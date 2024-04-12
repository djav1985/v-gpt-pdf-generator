# main.py

# Importing necessary modules and libraries
import os
import pdfkit
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, FileResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .pdf_generator import generate_pdf  # Ensure correct import path
from cleanup import delete_old_pdfs
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Initialize the FastAPI app
app = FastAPI()

# Environment variables are now assumed to be set directly via Docker or another environment manager
API_KEY = os.getenv("API_KEY", "default_api_key_if_none_provided")
BASE_URL = os.getenv("BASE_URL", "http://localhost")

# Class for handling API key authentication
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get('Authorization')
        if not api_key or api_key != API_KEY:
            return JSONResponse(status_code=403, content={"message": "Invalid or missing API Key"})
        response = await call_next(request)
        return response

# Add the authentication middleware to the app
app.add_middleware(AuthMiddleware)

# Setup a background scheduler for deleting old PDFs
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_pdfs, 'interval', days=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Class for handling create PDF request data
class CreatePDFRequest(BaseModel):
    html_content: str
    css_content: str
    output_filename: str

# Endpoint for creating a new PDF
@app.post("/create")
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks):
    output_path = f"/app/downloads/{request.output_filename}.pdf"
    background_tasks.add_task(
        generate_pdf,
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )
    return {"message": "PDF creation started successfully", "download_url": f"{BASE_URL}/download/{request.output_filename}.pdf"}

# Endpoint for downloading a created PDF
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = f"/app/downloads/{filename}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=f"{filename}.pdf", media_type='application/pdf')
