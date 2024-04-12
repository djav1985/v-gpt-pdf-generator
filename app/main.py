import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Assuming pdf_generator and cleanup are in the same directory or correctly installed as packages
from pdf_generator import generate_pdf
from cleanup import delete_old_pdfs

BASE_URL = os.getenv("BASE_URL", "http://localhost")

app = FastAPI(
    title="PDF Generation API",
    version="0.1.0",
    description="API for generating and managing PDFs",
    servers=[{"url": BASE_URL, "description": "Base API server"}]
)

scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_pdfs, 'interval', days=1)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

class CreatePDFRequest(BaseModel):
    html_content: str = Field(..., example="<html><body><p>Hello World</p></body></html>")
    css_content: str = Field(..., example="p { color: red; }")
    output_filename: str = Field(..., example="example.pdf")

class CreatePDFResponse(BaseModel):
    message: str
    download_url: str

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
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
