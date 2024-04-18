# Importing required libraries and modules
import os
import requests
from weasyprint import HTML, CSS
from fastapi import HTTPException
from bs4 import BeautifulSoup

# Function to convert a URL to a PDF
def convert_url_to_pdf(url: str, output_path: str):
    """
    This function fetches the HTML content from a given URL, modifies it by removing <h1> to <h6> and <p>
    tags that are not inside <footer> or <aside> tags, and then converts it into a PDF document.

    Args:
        url (str): The URL of the webpage to be converted.
        output_path (str): The path where the generated PDF will be saved.

    Returns:
        None
    """
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

        # Generate PDF from the modified HTML content
        modified_html = str(soup)
        HTML(string=modified_html).write_pdf(output_path)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert URL to PDF: {str(e)}")

# Function to generate a PDF from provided HTML and CSS content
def generate_pdf(html_content: str, css_content: str, output_path: str):
    """
    Generates a PDF document from provided HTML and CSS content.
    Args:
        html_content (str): HTML content to convert into PDF.
        css_content (str): CSS content for styling the HTML.
        output_path (str): Path where the generated PDF will be saved.
    """
    from weasyprint import HTML, CSS
    if css_content:
        html_content = f"<style>{css_content}</style>{html_content}"
    try:
        HTML(string=html_content).write_pdf(output_path, stylesheets=[CSS(string=css_content)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Load configuration from environment variables
def load_configuration():
    """
    This function loads the configuration settings from environment variables.

    Returns:
        BASE_URL (str): The base URL for the application, defaulting to "http://localhost".
        API_KEY (str): The API key for authentication.
    """
    # The base URL for the application, defaulting to "http://localhost"
    BASE_URL = os.getenv("BASE_URL", "http://localhost")

    # The API key for authentication
    API_KEY = os.getenv("API_KEY")

    return BASE_URL, API_KEY
