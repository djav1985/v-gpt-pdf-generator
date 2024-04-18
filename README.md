# FastAPI Application with Docker

This repository contains a FastAPI application designed to generate PDFs from HTML and CSS content. It's packaged with Docker and orchestrated using Docker Compose, simplifying development and deployment processes.

## Features

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Docker**: Containerization of the application ensuring consistency across various development and deployment environments.
- **Docker Compose**: Simplifies the setup of local development and services needed to run the application.

## Prerequisites

Before you can run this application, you'll need:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

These instructions will cover usage information and for the docker container

### Setup

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/your-repository-name.git
cd your-repository-name
```

### Build & Run

To build and run the application in a Docker container, execute:

```bash
docker-compose up --build
```

This command builds the Docker image if it hasn't been built and starts the containers specified in the `docker-compose.yml` file.

### Accessing the Application

Once the application is running, you can access:
- The API at: [http://localhost:8000](http://localhost:8000)
- Swagger UI Documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc Documentation at: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### API Endpoints

- `POST /create`: Endpoint to create a PDF from HTML and CSS.
- `POST /convert_urls`: Endpoint to convert given URLs into PDFs.
- `GET /`: Serves the `index.html` file (not shown in API docs).

## Development

### Environment Variables

Configure the following environment variables before starting the application:

- `API_KEY`: The API key for accessing the secured endpoints. (Optional)
- `BASE_URL`: The base URL for the application. Defaults to `http://localhost`.

### Adding New Dependencies

If you need to add new Python packages:

1. Add the package to the `requirements.txt` file.
2. Rebuild the Docker image:

```bash
docker-compose up --build
```

## Testing

Run tests directly within your Docker container:

```bash
docker-compose exec web pytest
```

## Deployment

To deploy this application, use the provided `Dockerfile` and `docker-compose.yml` files to manage and scale the application across different environments.
