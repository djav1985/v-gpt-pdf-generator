import os
import json
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Assuming pdf_generator and cleanup are in the same directory or correctly installed as packages
from pdf_generator import generate_pdf
from cleanup import delete_old_pdfs

API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost")

api_key_header = APIKeyHeader(name="Authorization")

app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="API for generating and managing PDFs",
    servers=[{"url": BASE_URL, "description": "Base API server"}]
)

@app.on_event("startup")
def startup_event():
    print(f"API Key on startup: {API_KEY}")

scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_pdfs, 'interval', days=1)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        api_key = request.headers.get('Authorization')
        if not api_key or api_key != API_KEY:
            return JSONResponse(status_code=403, content={"message": "Invalid or missing API Key"})
        
        return await call_next(request)

app.add_middleware(AuthMiddleware)

def api_key_dependency(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

class CreatePDFRequest(BaseModel):
    html_content: str = Field(..., example="<html><body><p>Hello World</p></body></html>")
    css_content: str = Field(..., example="p { color: red; }")
    output_filename: str = Field(..., example="example.pdf")

class CreatePDFResponse(BaseModel):
    message: str
    download_url: str

@app.post("/create", response_model=CreatePDFResponse, dependencies=[Depends(api_key_dependency)])
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

@app.get("/download/{filename}", responses={
    200: {
        "content": {"application/pdf": {}},
        "description": "Returns the requested PDF file."
    },
    404: {
        "description": "PDF file not found"
    }
}, dependencies=[Depends(api_key_dependency)])
async def download_pdf(filename: str):
    file_path = f"/app/downloads/{filename}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
