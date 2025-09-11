from pathlib import Path
import pytest
from fastapi.testclient import TestClient

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
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.setenv("BASE_URL", "http://test")

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
    assert data["url"].startswith("http://test")
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].suffix == ".pdf"


def test_create_pdf_endpoint_invalid_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
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
