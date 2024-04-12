# FastAPI PDF Generator

This repository contains a FastAPI application designed to generate PDFs from HTML and CSS content and manage PDF storage with an automated cleanup task. The application uses `pdfkit` for PDF generation and `APScheduler` for scheduling PDF file cleanup in the background.

## Features

- **PDF Generation**: Convert HTML and CSS into PDF files.
- **API Key Authentication**: Secure API endpoints using API key authentication.
- **Automated Cleanup**: Scheduled deletion of PDF files older than 3 days to manage disk space.
- **OpenAPI Documentation**: Automatic OpenAPI schema generation for easy API documentation and testing.

## Usage

### Creating a PDF

Send a POST request to /create with HTML and CSS content to generate a PDF. The API will return a URL to download the generated PDF.

```bash
curl -X POST "http://localhost/create" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"html_content\": \"<p>Hello World</p>\", \"css_content\": \"p { color: red; }\", \"output_filename\": \"example\"}"
```

### Downloading a PDF

Access the generated PDF via the /download/{filename} endpoint.

```bash
curl -X GET "http://localhost/download/example.pdf"
```

## API Documentation

Visit [http://localhost/docs](http://localhost/docs) to view the Swagger UI where you can test and document the API endpoints.

## Scheduled Cleanup

The application is configured to automatically delete PDF files older than 3 days. This task is scheduled to run once every day using a cron job within the Docker environment.