from pathlib import Path

import pytest
from fastapi import HTTPException

import app.dependencies as deps


@pytest.mark.asyncio
async def test_generate_pdf_success_extra_css(monkeypatch, tmp_path):
    captured = {}

    class DummyHTML:
        def __init__(self, string):
            captured["string"] = string

        def write_pdf(self, target):
            Path(target).write_bytes(b"PDF")

    def fake_highlight(code, lexer, formatter):
        return f"<div class='highlight'>{code}</div>"

    class DummyFormatter:
        def __init__(self, style="default"):
            pass

        def get_style_defs(self, selector):
            return ".highlight{}"

    monkeypatch.setattr(deps, "HTML", DummyHTML)
    monkeypatch.setattr(deps, "highlight", fake_highlight)
    monkeypatch.setattr(deps, "HtmlFormatter", DummyFormatter)
    monkeypatch.setattr(deps, "get_lexer_by_name", lambda name: None)
    monkeypatch.setattr(deps, "guess_lexer", lambda code: None)

    output = tmp_path / "out.pdf"

    await deps.generate_pdf(
        pdf_title="Title",
        body_content="<p>Hello</p>",
        css_content="p{color:blue;}",
        output_path=output,
        contains_code=False,
    )

    assert output.exists()
    assert "p{color:blue;}" in captured["string"]
    assert "font-family" in captured["string"]


@pytest.mark.asyncio
async def test_generate_pdf_highlights_code(monkeypatch, tmp_path):
    captured = {}
    highlight_called = {}

    class DummyHTML:
        def __init__(self, string):
            captured["string"] = string

        def write_pdf(self, target):
            Path(target).write_bytes(b"PDF")

    def fake_highlight(code, lexer, formatter):
        highlight_called["called"] = True
        return f"<div class='highlight'>{code}</div>"

    class DummyFormatter:
        def __init__(self, style="default"):
            pass

        def get_style_defs(self, selector):
            return ".highlight{}"

    monkeypatch.setattr(deps, "HTML", DummyHTML)
    monkeypatch.setattr(deps, "highlight", fake_highlight)
    monkeypatch.setattr(deps, "HtmlFormatter", DummyFormatter)
    monkeypatch.setattr(deps, "get_lexer_by_name", lambda name: None)
    monkeypatch.setattr(deps, "guess_lexer", lambda code: None)

    output = tmp_path / "out.pdf"
    body = '<pre><code class="language-python">print("hi")</code></pre>'

    await deps.generate_pdf(
        pdf_title="Title",
        body_content=body,
        css_content=None,
        output_path=output,
        contains_code=True,
    )

    assert output.exists()
    assert highlight_called.get("called")
    assert "<div class='highlight'>print(\"hi\")</div>" in captured["string"]


@pytest.mark.asyncio
async def test_generate_pdf_error(monkeypatch, tmp_path):
    class FailingHTML:
        def __init__(self, string):
            pass

        def write_pdf(self, target):
            raise ValueError("fail")

    monkeypatch.setattr(deps, "HTML", FailingHTML)

    with pytest.raises(HTTPException) as exc:
        await deps.generate_pdf(
            pdf_title="Title",
            body_content="<p>Hello</p>",
            css_content=None,
            output_path=tmp_path / "out.pdf",
            contains_code=False,
        )

    assert exc.value.status_code == 500
