<p align="center">
  <img src="v-gpt-pdf-generator.png" width="60%" alt="project-logo">
</p>
<p align="center">
    <h1 align="center">V-GPT-PDF-GENERATOR</h1>
</p>
<p align="center">
    <em>Effortless PDF Creation from HTML & CSS Magic</em>
</p>
<p align="center">
	<!-- local repository, no metadata badges. -->
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=flat-square&logo=Pydantic&logoColor=white" alt="Pydantic">
	<img src="https://img.shields.io/badge/YAML-CB171E.svg?style=flat-square&logo=YAML&logoColor=white" alt="YAML">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/AIOHTTP-2C5BB4.svg?style=flat-square&logo=AIOHTTP&logoColor=white" alt="AIOHTTP">
	<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat-square&logo=Docker&logoColor=white" alt="Docker">
	<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=FastAPI&logoColor=white" alt="FastAPI">
</p>

<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [📍 Overview](#-overview)
- [🧩 Features](#-features)
- [🗂️ Repository Structure](#️-repository-structure)
- [📦 Modules](#-modules)
- [🚀 Getting Started](#-getting-started)
  - [⚙️ Installation](#️-installation)
  - [🤖 Usage](#-usage)
  - [🧪 Tests](#-tests)
- [🛠 Project Roadmap](#-project-roadmap)
- [🎗 License](#-license)
</details>
<hr>

## 📍 Overview

The v-gpt-pdf-generator is an efficient, FastAPI-based web service designed to convert HTML and CSS content into high-quality PDFs. By leveraging WeasyPrint for PDF generation, it facilitates asynchronous operations using Aiohttp and Aiofiles, ensuring fast and scalable performance. The application is containerized for ease of deployment, incorporating robust dependency management, data validation, and security protocols. Ideal for developers needing automated PDF generation via API endpoints, this project stands out for its seamless integration, error handling, and accessibility, thus enhancing operational efficiency and resource management in web applications.

---

## 🧩 Features

|    |   Feature         | Description |
|----|-------------------|---------------------------------------------------------------|
| ⚙️  | **Architecture**  | The project uses a microservice architecture with FastAPI for the web framework, and Docker for containerization, ensuring modularity and scalability. |
| 🔩 | **Code Quality**  | The codebase is well-structured, adhering to best practices with Pydantic for data validation and type checking, ensuring maintainability and readability. |
| 📄 | **Documentation** | Comprehensive documentation with clear explanations of dependencies and setup instructions in `requirements.txt`, `docker-compose.yml`, and `Dockerfile`. In-code comments provide additional clarity. |
| 🔌 | **Integrations**  | Key integrations include FastAPI for the web server, Uvicorn for ASGI server functionality, WeasyPrint for PDF generation, and BeautifulSoup4 for HTML parsing and scraping. |
| 🧩 | **Modularity**    | Highly modular with separate modules for routes, dependencies, and models, allowing easy maintenance and scalability. |
| 🧪 | **Testing**       | No explicit mention of testing frameworks, but the modular architecture allows seamless integration of unit and integration testing tools like Pytest. |
| ⚡️  | **Performance**   | Optimized for performance using asynchronous I/O with Aiohttp and Aiofiles. Runs efficiently within Docker containers using a slim Python image. |
| 🛡️ | **Security**      | API key validation for controlling access, and dependency management ensures compliance with security standards. Regular cleanup tasks enhance stability. |
| 📦 | **Dependencies**  | Dependencies include FastAPI, Uvicorn, WeasyPrint, Pydantic, Aiohttp, Aiofiles, and BeautifulSoup4, detailed in `requirements.txt`. |
| 🚀 | **Scalability**   | Designed to scale with Docker and Docker Compose, supporting containerized deployment and orchestration, with efficient resource management. |

---

## 🗂️ Repository Structure

```sh
└── v-gpt-pdf-generator/
    ├── Dockerfile
    ├── README.md
    ├── app
    │   ├── __init__.py
    │   ├── dependencies.py
    │   ├── main.py
    │   ├── models.py
    │   └── routes
    ├── docker-compose.yml
    ├── images
    │   └── header.png
    └── requirements.txt
```

---

## 📦 Modules

<details closed><summary>.</summary>

| File                                     | Summary                                                                                                                                                                                                                                                                                                              |
| ---                                      | ---                                                                                                                                                                                                                                                                                                                  |
| [requirements.txt](requirements.txt)     | Defines project dependencies, including FastAPI for web framework functionality, Uvicorn for ASGI server capability, WeasyPrint for PDF generation, Pydantic for data validation, Aiohttp for asynchronous HTTP requests, Aiofiles for asynchronous file handling, and BeautifulSoup4 for HTML parsing and scraping. |
| [docker-compose.yml](docker-compose.yml) | Facilitate containerized deployment and orchestration of the GPT PDF generator service, specifying service configurations, network settings, environment variables, and storage volumes to ensure scalability, persistence, and efficient resource management within the larger system architecture.                 |
| [Dockerfile](Dockerfile)                 | Builds a Docker image for the v-gpt-pdf-generator application, installing necessary dependencies and preparing the environment to run a FastAPI app with Uvicorn, optimized for efficiency and performance. Ensures compatibility with WeasyPrint and related libraries, exposing port 8888 for external access.     |

</details>

<details closed><summary>app</summary>

| File                                   | Summary                                                                                                                                                                                                                                                                                                                                 |
| ---                                    | ---                                                                                                                                                                                                                                                                                                                                     |
| [main.py](app/main.py)                 | Main.py establishes a FastAPI application for generating PDFs from HTML and CSS, defines essential application metadata, and includes routers for endpoint management. It also configures a static files directory to serve the generated PDFs, ensuring efficient file handling and accessibility within the application architecture. |
| [dependencies.py](app/dependencies.py) | Manage dependencies for API key validation, PDF generation, and folder cleanup within the PDF generator application. Ensure compliance with security standards and automate routine maintenance tasks to enhance application stability and performance.                                                                                 |
| [models.py](app/models.py)             | Define the structure for PDF creation requests by specifying HTML and optional CSS content for conversion, along with an optional output filename. Simplify the process of generating well-formatted PDFs from structured HTML content within the repositorys architecture.                                                             |

</details>

<details closed><summary>app.routes</summary>

| File                              | Summary                                                                                                                                                                                                                                                                                                 |
| ---                               | ---                                                                                                                                                                                                                                                                                                     |
| [create.py](app/routes/create.py) | Facilitates the generation of custom PDFs through an API endpoint, leveraging HTML and CSS inputs. Integrates dependencies for PDF creation and ensures proper handling of filenames and output paths. Provides a URL for accessing the generated PDF and manages error handling for robust operations. |

</details>

---

## 🚀 Getting Started

**System Requirements:**

* **Python**: `version 3.10`

### ⚙️ Installation

<h4>From <code>source</code></h4>

> 1. Clone the v-gpt-pdf-generator repository:
>
> ```console
> $ git clone ../v-gpt-pdf-generator
> ```
>
> 2. Change to the project directory:
> ```console
> $ cd v-gpt-pdf-generator
> ```
>
> 3. Install the dependencies:
> ```console
> $ pip install -r requirements.txt
> ```

### 🤖 Usage

<h4>From <code>source</code></h4>

> Run v-gpt-pdf-generator using the command below:
> ```console
> $ python main.py
> ```

### 🧪 Tests

> Run the test suite using the command below:
> ```console
> $ pytest
> ```

---

## 🛠 Project Roadmap

- [X] `► INSERT-TASK-1`
- [ ] `► INSERT-TASK-2`
- [ ] `► ...`

---

## 🎗 License

This project is protected under the MIT Licence

---

[**Return**](#-overview)

---
