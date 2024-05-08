# /routes/dify.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import aiohttp
from fastapi.responses import JSONResponse
from fastapi.background import BackgroundTasks

# Importing local modules
from functions import AppConfig, scrape_site, get_api_key  # Adjusted import

# Create a router instance
dify_router = APIRouter()

# Load configuration on startup
config = AppConfig()


class KBCreationRequest(BaseModel):
    """Model for creating a Knowledge Base."""

    name: str = Field(..., description="Name of the knowledge base to be created.")


class KBSubmissionRequest(BaseModel):
    """Model for submitting a document."""

    website_url: str = Field(..., description="URL of the website to scrape.")
    dataset_id: str = Field(
        ..., description="ID of the dataset to submit the document to."
    )
    indexing_technique: Optional[str] = Field(
        "high_quality", description="Indexing technique to be used."
    )


@dify_router.post("/create-kb/", operation_id="create_kb")
async def create_new_kb(
    request: KBCreationRequest, api_key: str = Depends(get_api_key)
):
    api_url = f"{config.KB_BASE_URL}/v1/datasets"
    headers = {
        "Authorization": f"Bearer {config.KB_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"name": request.name}
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status == 200:
                # Parse the response data to get the ID
                response_data = await response.json()
                kb_id = response_data.get("id", "")
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": f"Knowledge Base '{request.name}' created successfully.",
                        "id": kb_id,
                    },
                )
            else:
                # Handle non-200 responses
                response_data = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"API request failed to create the KB. Details: {response_data}",
                )


@dify_router.post("/kb-scraper/", operation_id="web_to_kb")
async def scrape_to_kb(
    request: KBSubmissionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    # Add task with correct parameters
    background_tasks.add_task(scrape_site, request.website_url, request.dataset_id)
    return {
        "message": f"Scraping {request.website_url} to Knowledge Base {request.dataset_id} initiated. Check dataset for updates."
    }
