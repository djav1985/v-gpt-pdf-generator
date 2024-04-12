import os
import pdfkit
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Assuming pdf_generator and cleanup are in the same directory or correctly installed as packages
from pdf_generator import generate_pdf
from cleanup import delete_old_pdfs

# Environment variables are now assumed to be set directly via Docker or another environment manager
API_KEY = os.getenv("API_KEY", "default_api_key_if_none_provided")
BASE_URL = os.getenv("BASE_URL", "http://localhost")

# Initialize the FastAPI application with metadata
app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="API for generating and managing PDFs",
    servers=[{"url": BASE_URL, "description": "Base API server"}]
)

@app.on_event("startup")
def startup_event():
    api_key = os.getenv("API_KEY")
    print(f"API Key on startup: {api_key}")

# Setup a background scheduler for deleting old PDFs
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_pdfs, 'interval', days=1)
scheduler.start()

# Ensure that when the application exits, the scheduler is properly shutdown
atexit.register(lambda: scheduler.shutdown())

# Class for handling API key authentication
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Define a list of routes that don't require authentication
        paths = ["/docs", "/openapi.json", "/redoc"]
        if request.url.path in paths:
            # Skip authentication for documentation and open API JSON
            return await call_next(request)

        # API key validation
        api_key = request.headers.get('Authorization')
        if not api_key or api_key != API_KEY:
            return JSONResponse(status_code=403, content={"message": "Invalid or missing API Key"})
        
        return await call_next(request)

# Add the authentication middleware to the app
app.add_middleware(AuthMiddleware)

# Pydantic model to validate incoming data for the PDF creation
class CreatePDFRequest(BaseModel):
    html_content: str = Field(..., example="<html><body><p>Hello World</p></body></html>")
    css_content: str = Field(..., example="p { color: red; }")
    output_filename: str = Field(..., example="example.pdf")

class CreatePDFResponse(BaseModel):
    message: str
    download_url: str

# Endpoint for creating a new PDF
@app.post("/create", response_model=CreatePDFResponse)
async def create_pdf(request: CreatePDFRequest, background_tasks: BackgroundTasks):
    output_path = f"/app/downloads/{request.output_filename}.pdf"
    background_tasks.add_task(
        generate_pdf,
        html_content=request.html_content,
        css_content=request.css_content,
        output_path=output_path
    )
    return {
        "message": "PDF creation started successfully", 
        "download_url": f"{BASE_URL}/download/{request.output_filename}"
    }

# Endpoint for downloading a created PDF
@app.get("/download/{filename}", responses={
    200: {
        "content": {"application/pdf": {}},
        "description": "Returns the requested PDF file."
    },
    404: {
        "description": "PDF file not found"
    }
})
async def download_pdf(filename: str):
    file_path = f"/app/downloads/{filename}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
