# Importing required libraries and modules
import os
import requests
from weasyprint import HTML, CSS
from fastapi import HTTPException
from bs4 import BeautifulSoup

# Function to convert a URL to a PDF

def convert_url_to_pdf(url: str, output_path: str):
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        html_content = response.text

        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <footer> and <aside> tags and mark them to skip
        skip_tags = soup.find_all(['footer', 'aside'])

        # Find and remove <h1> to <h6>, <p> not within <footer> or <aside>
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            if not any(parent in skip_tags for parent in tag.parents):
                tag.decompose()

        # Define the default CSS
        default_css = "body { font-family: 'Arial', sans-serif; } h1, h2, h3, h4, h5, h6 { color: #66cc33; } p { margin: 0.5em 0; } a { color: #66cc33; text-decoration: none; }"

        # Generate PDF from the modified HTML content with the custom CSS
        modified_html = str(soup)
        HTML(string=modified_html).write_pdf(output_path, stylesheets=[CSS(string=default_css)])

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert URL to PDF: {str(e)}")


# Load configuration from environment variables
def load_configuration():
    # The base URL for the application, defaulting to "http://localhost"
    BASE_URL = os.getenv("BASE_URL", "http://localhost")

    # The API key for authentication
    API_KEY = os.getenv("API_KEY")

    return BASE_URL, API_KEY
