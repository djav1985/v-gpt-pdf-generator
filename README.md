<p align="center">
  <img src="v-gpt-pdf-generator.png" width="60%" alt="project-logo">
</p>
<p align="center">
    <h1 align="center"></h1>
</p>
<p align="center">
    <em>Transform Ideas into PDFs, Effortlessly!</em>
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
- [🛠 Project Changelog](#-project-changelog)
- [🎗 License](#-license)

</details>
<hr>

## 📍 Overview

The project is a robust PDF Generation API built on FastAPI, designed to streamline the creation of PDF documents from HTML content. It offers a user-friendly interface that allows users to submit requests and generate customized PDFs while ensuring secure access through API key validation. By leveraging containerization with Docker, the application ensures seamless deployment and operation, facilitating efficient scaling and management. The value proposition lies in its ability to provide high-quality, customizable document generation capabilities, making it an essential tool for developers needing to integrate PDF functionalities into their applications while maintaining a clean and organized codebase.

---

## 🧩 Features

|    |   Feature         | Description |
|----|-------------------|---------------------------------------------------------------|
| ⚙️  | **Architecture**  | A microservice architecture utilizing FastAPI for web services and asynchronous capabilities. Docker containers orchestrate the PDF generation service, enhancing deployment and scalability. |
| 🔩 | **Code Quality**  | The codebase follows PEP 8 style guidelines with clear variable names, modular functions, and consistent formatting. It emphasizes clean code practices, improving readability and maintainability. |
| 📄 | **Documentation** | Documentation is comprehensive, detailing setup with `requirements.txt`, `Dockerfile`, and `docker-compose.yml`. In-line comments and structured organization guide users through the core functionalities. |
| 🔌 | **Integrations**  | Essential integrations include aiohttp for asynchronous HTTP requests, FastAPI for building APIs, and WeasyPrint for PDF generation. These components facilitate seamless data handling and PDF services. |
| 🧩 | **Modularity**    | The codebase is highly modular, with separate files for routing, models, and dependencies. This structure promotes reusability and easier testing, allowing developers to update components independently. |
| ⚡️  | **Performance**   | Optimized for high efficiency, the application handles multiple requests concurrently with FastAPI, minimizing response times and resource usage through asynchronous programming. |
| 🛡️ | **Security**      | Employs API key validation and secure access measures. Techniques like input validation and error handling safeguard against common vulnerabilities during PDF generation. |
| 📦 | **Dependencies**  | Key dependencies include FastAPI, WeasyPrint, Pydantic for data validation, aiofiles for file handling, and uvicorn for running the application, ensuring robust functionality and performance. |
| 🚀 | **Scalability**   | Designed to scale effectively with containerization using Docker. FastAPI enables asynchronous processing, allowing the application to manage increased loads and user requests without degradation of performance. |

---

## 🗂️ Repository Structure

```sh
└── /
    ├── Dockerfile
    ├── README.md
    ├── app
    │   ├── __init__.py
    │   ├── dependencies.py
    │   ├── main.py
    │   ├── models.py
    │   └── routes
    │       ├── __init__.py
    │       └── create.py
    ├── docker-compose.yml
    ├── requirements.txt
    └── v-gpt-pdf-generator.png
```

---

## 📦 Modules

<details closed><summary>.</summary>

| File                                     | Summary                                                                                                                                                                                                                                                                                                                                                                         |
| ---                                      | ---                                                                                                                                                                                                                                                                                                                                                                             |
| [requirements.txt](requirements.txt)     | Defines essential dependencies for the application, ensuring compatibility and functionality of key libraries. By incorporating FastAPI, WeasyPrint, and other critical packages, it enables robust web service capabilities, document generation, and efficient data handling, aligning seamlessly with the repositorys architecture to support the overall application goals. |
| [docker-compose.yml](docker-compose.yml) | Facilitates the orchestration of a PDF generation service within the repositorys architecture by defining the containerized environment. It configures essential parameters such as network settings, environment variables, and persistent storage, ensuring seamless integration and operation of the PDF generation application.                                             |
| [Dockerfile](Dockerfile)                 | Facilitates the creation and deployment of a FastAPI application by establishing a multi-stage Docker environment. It efficiently manages Python dependencies, integrates necessary system libraries for rendering, and configures runtime parameters while ensuring the application is accessible on port 8888, aligning with the overall architecture of the repository.      |

</details>

<details closed><summary>app</summary>

| File                                   | Summary                                                                                                                                                                                                                                                                                                                                             |
| ---                                    | ---                                                                                                                                                                                                                                                                                                                                                 |
| [main.py](app/main.py)                 | Facilitates the core functionality of the PDF Generation API by establishing a FastAPI application, integrating routing for PDF creation, and serving generated PDFs through a dedicated static files directory. This setup enhances the repositorys architecture by providing a scalable and organized approach to handle PDF generation requests. |
| [dependencies.py](app/dependencies.py) | Facilitates asynchronous PDF generation and cleanup tasks within the repository. It crafts customized HTML templates from content and CSS, integrates code highlighting, and manages a downloads folder by removing outdated files. Additionally, it ensures API key validation for secure access to the application.                               |
| [models.py](app/models.py)             | Defines a data model for generating PDFs, ensuring structured input through required fields like title and body content, while allowing optional custom styling and filenames. This model seamlessly integrates with the applications architecture to facilitate user-friendly PDF creation from HTML content, enhancing overall functionality.     |

</details>

<details closed><summary>app.routes</summary>

| File                              | Summary                                                                                                                                                                                                                                                                                                                                                        |
| ---                               | ---                                                                                                                                                                                                                                                                                                                                                            |
| [create.py](app/routes/create.py) | Facilitates PDF generation by processing user requests and producing downloadable files. It ensures unique filename creation, integrates API key verification, and handles exceptions gracefully, enhancing the overall functionality of the application by linking user inputs with the PDF creation process effectively within the repositorys architecture. |

</details>

---

## 🚀 Getting Started

**System Requirements:**

* **Python**: `version 3.10`


### ⚙️ Installation

1. **Download the `docker-compose.yml` file**:  
   Save the provided `docker-compose.yml` file to your project directory.

2. **Edit Environment Variables**:  
   Open the `docker-compose.yml` file and set the environment variables according to your setup:

   ```yaml
   environment:
      BASE_URL: https://api.servicesbyv.com # Set this to your actual base URL
      ROOT_PATH: /pdf
      API_KEY: # Optional API key to connect to the API
      WORKERS: 1  # Number of Uvicorn workers; 1 is usually enough for personal use
      UVICORN_CONCURRENCY: 32  # Max connections; anything over this number is rejected
   ```

3. **Run the Docker Compose**:  
   Use the following command to start the service:

   ```bash
   docker-compose up
   ```

4. **(Optional) Run in Detached Mode**:  
   To run the containers in the background, use:

   ```bash
   docker-compose up -d
   ```

### 🤖 Usage

#### From `docker-compose`

1. **Access the OpenAPI Specifications**:  
   To get the OpenAPI specifications and integrate with your AI tool, navigate to:

   ```
   BASE_URL/openapi.json
   ```

   Replace `BASE_URL` with the actual URL of your application (e.g., `https://api.servicesbyv.com/pdf/openapi.json`).
   
---

## 🛠 Project Changelog

-  `► Added footer to pdfs`
-  `► improved page breaks`
-  `► Minor code improvements`

---

## 🎗 License

This project is protected under the [MIT License](./LICENSE).

---

[**Return**](#-overview)

---
