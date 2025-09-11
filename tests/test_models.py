import pytest
from pydantic import ValidationError

from app.models import CreatePDFRequest, CreatePDFResponse, ErrorResponse


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
        output_filename="File",
        contains_code=True,
    )
    assert req.css_content == "p{color:red;}"
    assert req.output_filename == "file.pdf"
    assert req.contains_code is True


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_pdf_title_validation(title):
    with pytest.raises(ValidationError):
        CreatePDFRequest(pdf_title=title, body_content="<p>x</p>")


@pytest.mark.parametrize(
    "body",
    ["", "   ", "<h1>bad</h1>", "<script>alert(1)</script>", "<form></form>"],
)
def test_body_content_validation(body):
    with pytest.raises(ValidationError):
        CreatePDFRequest(pdf_title="Title", body_content=body)


@pytest.mark.parametrize(
    "css",
    ["@import url('x')", "body{background:url('x')}", "<script></script>"],
)
def test_css_content_validation(css):
    with pytest.raises(ValidationError):
        CreatePDFRequest(pdf_title="Title", body_content="<p>x</p>", css_content=css)


@pytest.mark.parametrize(
    "filename",
    ["bad/name", "bad\\name", "bad name", "a" * 101],
)
def test_output_filename_invalid(filename):
    with pytest.raises(ValidationError):
        CreatePDFRequest(
            pdf_title="Title",
            body_content="<p>x</p>",
            output_filename=filename,
        )


def test_output_filename_sanitized():
    req = CreatePDFRequest(
        pdf_title="Title",
        body_content="<p>x</p>",
        output_filename=" My_File ",
    )
    assert req.output_filename == "my_file.pdf"


def test_extra_fields_forbidden_request():
    with pytest.raises(ValidationError):
        CreatePDFRequest(
            pdf_title="Title",
            body_content="<p>x</p>",
            unknown="oops",
        )


def test_extra_fields_forbidden_response_models():
    with pytest.raises(ValidationError):
        ErrorResponse(status=400, code="err", message="m", extra="x")
    with pytest.raises(ValidationError):
        CreatePDFResponse(results="ok", url="http://example.com", extra="x")
