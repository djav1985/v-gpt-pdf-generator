# Importing required libraries and modules
import os
import requests
from weasyprint import HTML, CSS
from fastapi import HTTPException

# Function to convert a URL to a PDF
def convert_url_to_pdf(url: str, output_path: str):
    """
    This function fetches the HTML content from a given URL and converts it into a PDF document.

    Args:
        url (str): The URL of the webpage to be converted.
        output_path (str): The path where the generated PDF will be saved.

    Returns:
        None
    """
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad requests
        html_content = response.text

        # Generate PDF from HTML content
        HTML(string=html_content).write_pdf(output_path)

    except Exception as e:
        print(f"Failed to convert {url} to PDF: {str(e)}")  # Log error


# Function to generate a PDF from provided HTML and CSS content
def generate_pdf(html_content, css_content, output_path):
    """
    This function generates a PDF document from provided HTML and CSS content.

    Args:
        html_content (str): The HTML content to be converted into PDF.
        css_content (str): The CSS content for styling the HTML.
        output_path (str): The path where the generated PDF will be saved.

    Returns:
        None
    """
    # If CSS content is provided, prepend it to the HTML content
    if css_content and css_content.strip():
        html_content = f"<style>{css_content}</style>{html_content}"

    # Generate the PDF using WeasyPrint
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
