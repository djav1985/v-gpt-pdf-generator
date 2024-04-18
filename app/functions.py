# Importing required libraries and modules
import os
import requests
from datetime import datetime, timedelta
from weasyprint import HTML, CSS
from fastapi import HTTPException, BackgroundTasks
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


# This function loads configuration from environment variables.
def load_configuration():
    # The base URL for the application, defaulting to "http://localhost"
    BASE_URL = os.getenv("BASE_URL", "http://localhost")
    # The API key for authentication
    DIFY_INTEGRATION = os.getenv("DIFY_INTEGRATION")
    API_KEY = os.getenv("API_KEY")
    KB_API_KEY = os.getenv("KB_API_KEY")
    KB_BASE_URL = os.getenv("KB_BASE_URL")

    unwanted_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif','.ico', '.svg', '.webp', '.heif', '.heic', '.css', '.js','.mp4', '.avi', '.mp3', '.wav', '.mov', '.pdf', '.docx','.xlsx', '.pptx', '.zip', '.rar', '.7z')

    return BASE_URL, API_KEY, KB_BASE_URL, KB_API_KEY, unwanted_extensions, DIFY_INTEGRATION

# Function to generate a PDF from provided HTML and CSS content
def generate_pdf(html_content: str, css_content: str, output_path: str):
    try:
        if css_content:
            html_content = f"<style>{css_content}</style>{html_content}"
        HTML(string=html_content).write_pdf(output_path, stylesheets=[CSS(string=css_content)])
    except Exception as e:
        print("Error occurred:", e)
        background_tasks["exception"] = str(e)

# Function to convert a URL to PDF
def convert_url_to_pdf_task(url: str, output_path: str, background_tasks: BackgroundTasks):
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        html_content = response.text if response.status_code == 200 else ""

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove content within <footer> and <aside> tags
        for tag in soup(['footer', 'aside']):
            tag.decompose()

        # Extract text from <h1> to <h6> and <p> tags, preserving HTML tags
        extracted_content = ""
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            extracted_content += str(tag)

        # Write extracted content to PDF
        default_css = "body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }"
        HTML(string=extracted_content).write_pdf(output_path, stylesheets=[CSS(string=default_css)])
    except Exception as e:
        print("Error occurred:", e)
        background_tasks["exception"] = str(e)

# This function cleans up the downloads folder by removing files older than 7 days.
def cleanup_downloads_folder(folder_path: str):
    try:
        now = datetime.now()
        age_limit = now - timedelta(days=7)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mod_time < age_limit:
                    os.remove(file_path)
    except:
        pass  # Silently ignore any failures

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
    main_domain = urlparse(initial_url).netloc.split('.')[-2] + '.' + urlparse(initial_url).netloc.split('.')[-1]  # This will capture something like vontainment.com

    try:
        while queue:
            current_url = queue.pop()
            print("Current URL:", current_url)
            if current_url in visited:
                continue
            visited.add(current_url)
            print("Visiting URL:", current_url)
            html_content = await fetch_url(current_url, session, unwanted_extensions)
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
                href_parsed = urlparse(href)
                href_domain = href_parsed.netloc.split('.')[-2] + '.' + href_parsed.netloc.split('.')[-1]

                if href.startswith('http') and href_domain == main_domain and href not in visited and href not in queue:
                    if not any(href.endswith(ext) for ext in unwanted_extensions):
                        print("Adding URL to queue:", href)
                        queue.add(href)
    except Exception as e:
        print("Exception occurred during scraping:", e)


# Asynchronous function to submit data to KB API
async def submit_to_kb_api(url, text, dataset_id, indexing_technique, session):
    try:
        print("Submitting to KB API...")
        api_url = f"{os.getenv('KB_BASE_URL')}/v1/datasets/{dataset_id}/document/create_by_text"
        headers = {
            "Authorization": f"Bearer {os.getenv('KB_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": urlparse(url).path.split('/')[-1].replace('_', '-') or urlparse(url).netloc.replace('_', '-'),
            "text": text,
            "indexing_technique": indexing_technique,
            "process_rule": {"mode": "automatic"}
        }

        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                # Silently ignore any errors.
                pass
            print("Response status:", response.status)
    except Exception as e:
        print("Exception occurred during submission to KB API:", e)
        # This will catch any other exceptions that might occur during the posting process
        pass
