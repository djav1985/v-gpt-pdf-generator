# Importing required libraries and modules
import os
import aiohttp
from aiohttp import ClientSession
from pathlib import Path
from datetime import datetime, timedelta
from weasyprint import HTML, CSS
from fastapi import HTTPException, BackgroundTasks
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class AppConfig:
    def __init__(self):
        self.BASE_URL = os.getenv("BASE_URL", "http://localhost")
        self.API_KEY = os.getenv("API_KEY")
        self.KB_API_KEY = os.getenv("KB_API_KEY")
        self.KB_BASE_URL = os.getenv("KB_BASE_URL")
        self.DIFY = os.getenv("DIFY")
        self.unwanted_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.ico', '.svg', '.webp',
                                    '.heif', '.heic', '.css', '.js', '.mp4', '.avi', '.mp3', '.wav', '.mov', '.pdf',
                                    '.docx', '.xlsx', '.pptx', '.zip', '.rar', '.7z')

config = AppConfig()

# PDF generation tasks
async def generate_pdf(html_content: str, css_content: str, output_path: Path):
    try:
        css = CSS(string=css_content) if css_content else CSS(string="body { font-family: Arial; }")
        HTML(string=html_content).write_pdf(target=output_path, stylesheets=[css])
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
        
async def convert_url_to_pdf_task(url: str, output_path: str):
    try:
        # Initiate an HTTP session and fetch the HTML content
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch URL: {url}, status code: {response.status}")
                    raise HTTPException(status_code=response.status, detail="Failed to fetch HTML content")

                html_content = await response.text()

                # Process the HTML content if successfully retrieved
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    for tag in soup(['footer', 'aside']):
                        tag.decompose()
                    extracted_content = "".join(str(tag) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']))

                    # Convert extracted content to PDF
                    css = CSS(string="body { font-family: Arial; color: #333; }")
                    output_file_path = Path(output_path)
                    HTML(string=extracted_content).write_pdf(target=output_file_path, stylesheets=[css])
                else:
                    print("No HTML content found to convert to PDF")
                    raise HTTPException(status_code=404, detail="No HTML content found to convert to PDF")
    except Exception as e:
        print(f"Error converting URL to PDF: {url}, error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting URL to PDF: {str(e)}")

# Function to clean up the downloads folder
def cleanup_downloads_folder(folder_path: str):
    try:
        now = datetime.now()
        age_limit = now - timedelta(days=7)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and datetime.fromtimestamp(os.path.getmtime(file_path)) < age_limit:
                os.remove(file_path)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")

async def submit_to_kb(url, text, dataset_id, session):
    api_url = f"{config.KB_BASE_URL}/v1/datasets/{dataset_id}/document/create_by_text"
    headers = {"Authorization": f"Bearer {config.KB_API_KEY}", "Content-Type": "application/json"}
    payload = {"name": url, "text": text, "indexing_technique": "high_quality"}
    try:
        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                print(f"Failed to submit data to KB, status code: {response.status}, url: {url}")
                raise HTTPException(status_code=response.status, detail=f"Failed to submit data to KB: {response.status}")
    except Exception as e:
        print(f"Exception when submitting to KB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Exception when submitting to KB: {str(e)}")

async def fetch_url(current_url, session):
    try:
        async with session.get(current_url) as response:
            if response.status == 200:
                if current_url.endswith(config.unwanted_extensions):
                    return None
                return await response.text()
            else:
                print(f"Failed to fetch URL: {current_url}, status code: {response.status}")
                return None
    except Exception as e:
        print(f"Exception fetching URL: {current_url}, error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Exception fetching URL: {current_url}, error: {str(e)}")

async def scrape_site(initial_url, session, dataset_id):
    print("Scraping site started...")
    queue = set([initial_url])
    visited = set()
    base_domain = urlparse(initial_url).netloc
    try:
        while queue:
            current_url = queue.pop()
            if current_url in visited:
                continue
            visited.add(current_url)
            html_content = await fetch_url(current_url, session)
            if html_content is None:
                continue
            soup = BeautifulSoup(html_content, 'html.parser')
            all_text = []
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                if not tag.find_parent(['footer', 'aside']):
                    text = tag.get_text(strip=True)
                    all_text.append(text)
            if all_text:
                await submit_to_kb(current_url, "\n".join(all_text), dataset_id, session)
            for link in soup.find_all('a', href=True):
                href = urljoin(current_url, link['href'])
                if href.startswith('http') and base_domain in urlparse(href).netloc and href not in visited:
                    if not any(href.endswith(ext) for ext in config.unwanted_extensions):
                        queue.add(href)
    except Exception as e:
        print(f"Error during site scraping for URL: {initial_url}, error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during site scraping: {str(e)}")
