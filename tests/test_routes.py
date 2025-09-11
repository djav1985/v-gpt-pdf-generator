from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import app.config as config
from app.models import CreatePDFResponse

Path("/app/downloads").mkdir(parents=True, exist_ok=True)

from app.main import app  # noqa: E402
import app.routes.create as create_module  # noqa: E402


@pytest.mark.asyncio
async def fake_generate_pdf(
    pdf_title,
    body_content,
    css_content,
    output_path,
    contains_code,
):
    Path(output_path).write_bytes(b"PDF")


def test_create_pdf_endpoint_success(monkeypatch, tmp_path):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    monkeypatch.setattr(config.settings, "BASE_URL", "http://test")

    def fake_path(path_str):
        assert path_str == "/app/downloads"
        return tmp_path

    monkeypatch.setattr(create_module, "Path", fake_path)
    monkeypatch.setattr(create_module, "generate_pdf", fake_generate_pdf)

    client = TestClient(app)

    payload = {
        "pdf_title": "Example PDF",
        "contains_code": False,
        "body_content": "<p>Hello World</p>",
    }

    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer secret"},
    )

    assert response.status_code == 200
    data = response.json()
    CreatePDFResponse.model_validate(data)
    assert data["results"].startswith("PDF generation is complete")
    assert data["url"].startswith("http://test")
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].suffix == ".pdf"


def test_create_pdf_endpoint_invalid_api_key(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    client = TestClient(app)
    payload = {
        "pdf_title": "Example PDF",
        "contains_code": False,
        "body_content": "<p>Hello World</p>",
    }
    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer wrong"},
    )
    assert response.status_code == 403
    assert response.json() == {
        "status": 403,
        "code": "invalid_api_key",
        "message": "Invalid or missing API key",
        "details": "Provide a valid API key in the Authorization header",
    }


def test_create_pdf_endpoint_with_code_and_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    monkeypatch.setattr(config.settings, "BASE_URL", "http://test")

    def fake_path(path_str):
        assert path_str == "/app/downloads"
        return tmp_path

    async def fake_generate_pdf(
        pdf_title, body_content, css_content, output_path, contains_code
    ):
        assert contains_code is True
        Path(output_path).write_bytes(b"PDF")

    monkeypatch.setattr(create_module, "Path", fake_path)
    monkeypatch.setattr(create_module, "generate_pdf", fake_generate_pdf)

    client = TestClient(app)
    payload = {
        "pdf_title": "Example PDF",
        "contains_code": True,
        "body_content": '<pre><code class="language-python">x=1</code></pre>',
        "output_filename": "custom",
    }
    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200
    data = response.json()
    CreatePDFResponse.model_validate(data)
    assert data["results"].startswith("PDF generation is complete")
    assert data["url"].startswith("http://test")
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name.startswith("custom")


def test_create_pdf_endpoint_with_uppercase_tags(monkeypatch, tmp_path):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    monkeypatch.setattr(config.settings, "BASE_URL", "http://test")

    def fake_path(path_str):
        assert path_str == "/app/downloads"
        return tmp_path

    async def fake_generate_pdf(
        pdf_title, body_content, css_content, output_path, contains_code
    ):
        assert contains_code is True
        Path(output_path).write_bytes(b"PDF")

    monkeypatch.setattr(create_module, "Path", fake_path)
    monkeypatch.setattr(create_module, "generate_pdf", fake_generate_pdf)

    client = TestClient(app)
    payload = {
        "pdf_title": "Example PDF",
        "contains_code": True,
        "body_content": '<PRE><CODE class="language-python">x=1</CODE></PRE>',
    }
    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200
    data = response.json()
    CreatePDFResponse.model_validate(data)
    assert data["results"].startswith("PDF generation is complete")
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].suffix == ".pdf"


def test_create_pdf_endpoint_generate_pdf_error(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")

    async def fail_generate_pdf(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(create_module, "generate_pdf", fail_generate_pdf)

    client = TestClient(app)
    payload = {
        "pdf_title": "Example PDF",
        "contains_code": False,
        "body_content": "<p>Hello World</p>",
    }
    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 500
    assert response.json() == {
        "status": 500,
        "code": "internal_server_error",
        "message": "Internal Server Error",
        "details": "boom",
    }


def test_create_pdf_endpoint_rejects_extra_fields(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    client = TestClient(app)
    payload = {
        "pdf_title": "Example PDF",
        "contains_code": False,
        "body_content": "<p>Hello World</p>",
        "unexpected": "value",
    }
    response = client.post(
        "/",
        json=payload,
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 422


def test_download_route_serves_file():
    test_file = Path("/app/downloads/test.pdf")
    test_file.write_bytes(b"PDF")
    client = TestClient(app)
    response = client.get(app.url_path_for("download_pdf", filename="test.pdf"))
    assert response.status_code == 200
    assert response.content == b"PDF"
    test_file.unlink()


def test_download_route_rejects_path_traversal():
    client = TestClient(app)
    response = client.get("/downloads/%2e%2e/etc/passwd")
    assert response.status_code == 400
