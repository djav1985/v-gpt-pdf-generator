from app.main import app


def test_openapi_metadata():
    schema = app.openapi()

    # Security scheme metadata
    http_bearer = schema["components"]["securitySchemes"]["HTTPBearer"]
    assert http_bearer["description"] == "Provide the API key as a Bearer token"
    assert http_bearer["bearerFormat"] == "API Key"

    # URL format in CreatePDFResponse
    url_schema = schema["components"]["schemas"]["CreatePDFResponse"]["properties"]["url"]
    assert url_schema["format"] == "uri"

    # Error responses reference ErrorResponse and include examples
    for status, detail in [("403", "Invalid or missing API key"), ("500", "Internal Server Error")]:
        resp = schema["paths"]["/"]["post"]["responses"][status]["content"]["application/json"]
        assert resp["schema"]["$ref"] == "#/components/schemas/ErrorResponse"
        assert resp["example"]["detail"] == detail

    # Download endpoint is documented
    assert "/downloads/{filename}" in schema["paths"]
