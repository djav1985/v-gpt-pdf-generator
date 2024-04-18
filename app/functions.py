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
        raise HTTPException(status_code=500, detail=str(e))

# Async function to fetch HTML content using aiohttp
async def fetch_html_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
    return ""

# Async function to convert a URL to PDF
async def convert_url_to_pdf_task(url: str, output_path: str):
    try:
        html_content = await fetch_html_content(url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup(['footer', 'aside']):
                tag.decompose()
            extracted_content = "".join(str(tag) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']))
            generate_pdf(extracted_content, "body { font-family: Arial; color: #333; }", output_path)
    except Exception as e:
        print("Error converting URL to PDF:", e)

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
        print("Cleanup error:", e)
        
async def fetch_url(current_url, session, unwanted_extensions):
    async with session.get(current_url) as response:
        if response.status == 200:
            if current_url.endswith(unwanted_extensions):
                return None
            return await response.text()
        else:
            return None

async def scrape_site(initial_url, session, unwanted_extensions):
    print("Scraping site started...")
    queue = set([initial_url])
    visited = set()
    base_domain = urlparse(initial_url).netloc
    try:
        while queue:
            current_url = queue.pop()
            print("Current URL:", current_url)
            if current_url in visited:
                continue
            visited.add(current_url)
            print("Visiting URL:", current_url)
            html_content = await fetch_url(current_url, session,  unwanted_extensions)
            if html_content is None:
                print("HTML content is None for URL:", current_url)
                continue
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                if not tag.find_parent(['footer', 'aside']):
                    text = tag.get_text(strip=True) + '\n'
                    yield current_url, text
            # Add new pages to the queue
            for link in soup.find_all('a', href=True):
                href = urljoin(current_url, link['href'])
                if href.startswith('http') and base_domain in href and href not in visited:
                    if not href.endswith(unwanted_extensions):
                        print("Adding URL to queue:", href)
                        queue.add(href)
    except Exception as e:
        print("Exception occurred during scraping:", e)
        pass  # Silently ignore any errors

# Async function to submit data to KB API
async def submit_to_kb(url, text, dataset_id, session):
    try:
        api_url = f"{config.KB_BASE_URL}/v1/datasets/{dataset_id}/document/create_by_text"
        headers = {"Authorization": f"Bearer {config.KB_API_KEY}", "Content-Type": "application/json"}
        payload = {"name": url, "text": text, "indexing_technique": "high_quality"}
        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                print("Failed to submit:", response.status)
    except Exception as e:
        print("API submission error:", e)
