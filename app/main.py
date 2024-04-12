# main.py

import os
import pdfkit
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks  # Core FastAPI and utility imports
from starlette.responses import FileResponse, JSONResponse  # Correct imports from starlette for response handling
from pydantic import BaseModel  # Import BaseModel for request body data validation
from starlette.middleware.base import BaseHTTPMiddleware  # Middleware base class
from apscheduler.schedulers.background import BackgroundScheduler  # Scheduler for tasks
import atexit  # Handle cleanup operations on exit

# Relative imports for local modules, ensure the directory structure supports this
from .pdf_generator import generate_pdf
from .cleanup import delete_old_pdfs

# Initialize the FastAPI application
app = FastAPI()

# Setup a background scheduler for deleting old PDFs
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_pdfs, 'interval', days=1)
scheduler.start()

# Ensure that when the application exits, the scheduler is properly shutdown
atexit.register(lambda: scheduler.shutdown())

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
