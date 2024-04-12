import os
import pdfkit
import json
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from pdf_generator import generate_pdf
from cleanup import delete_old_pdfs

API_KEY = os.getenv("API_KEY", "default_api_key_if_none_provided")
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

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request headers and body
        body = await request.body()
        headers = Headers(request.headers)

        # Attempt to decode JSON body for logging, if it fails, log raw body
        try:
            body_content = json.loads(body.decode())
            print(f"Request body: {json.dumps(body_content, indent=2)}")
        except json.JSONDecodeError:
            print(f"Request body (raw): {body.decode()}")

        print(f"Request headers: {dict(headers)}")
        print(f"Received request at {request.url}")

        # Process the request
        response = await call_next(request)

        # This section is optional: logging response details
        response_body = [chunk async for chunk in response.body_iterator]
        response_body = b''.join(response_body)
        try:
            response_content = json.loads(response_body.decode())
            print(f"Response body: {json.dumps(response_content, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response body (raw): {response_body.decode()}")

        # Restore response body for actual response
        response.body_iterator = iter([response_body])
        return response

app.add_middleware(RequestLogMiddleware)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        paths = ["/docs", "/openapi.json", "/redoc"]
        if request.url.path in paths:
            return await call_next(request)
        api_key = request.headers.get('Authorization')
        if not api_key or api_key != API_KEY:
            return JSONResponse(status_code=403, content={"message": "Invalid or missing API Key"})
        return await call_next(request)

app.add_middleware(RequestLogMiddleware)
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

@app.post("/create", response_model=CreatePDFResponse, tags=["PDF Generation"], dependencies=[Depends(api_key_dependency)])
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
}, tags=["PDF Generation"], dependencies=[Depends(api_key_dependency)])
async def download_pdf(filename: str):
    file_path = f"/app/downloads/{filename}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
