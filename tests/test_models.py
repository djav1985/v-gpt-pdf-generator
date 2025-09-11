import pytest
from pydantic import ValidationError

from app.models import CreatePDFRequest


def test_create_pdf_request_missing_fields():
    with pytest.raises(ValidationError):
        CreatePDFRequest(body_content="<p>x</p>")
    with pytest.raises(ValidationError):
        CreatePDFRequest(pdf_title="Title")


def test_create_pdf_request_optional_fields():
    req = CreatePDFRequest(
        pdf_title="Title",
        body_content="<p>x</p>",
        css_content="p{color:red;}",
        output_filename="file",
        contains_code=True,
    )
    assert req.css_content == "p{color:red;}"
    assert req.output_filename == "file"
    assert req.contains_code is True
