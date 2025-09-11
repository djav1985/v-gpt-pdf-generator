from app.main import app


def test_openapi_metadata():
    schema = app.openapi()

    assert schema["openapi"] == "3.1.0"
    assert len(schema["servers"]) == 3

    # Security scheme metadata
    http_bearer = schema["components"]["securitySchemes"]["HTTPBearer"]
    assert http_bearer["description"] == "Provide the API key as a Bearer token"
    assert http_bearer["bearerFormat"] == "API Key"

    # URL format in CreatePDFResponse
    url_schema = schema["components"]["schemas"]["CreatePDFResponse"]["properties"]["url"]
    assert url_schema["format"] == "uri"

    # Error responses reference ErrorResponse and include examples
    for status, code in [("403", "invalid_api_key"), ("500", "internal_server_error")]:
        resp = schema["paths"]["/"]["post"]["responses"][status]["content"]["application/json"]
        assert resp["schema"]["$ref"] == "#/components/schemas/ErrorResponse"
        assert resp["example"]["code"] == code

    # Download endpoint is documented and parameter described
    download = schema["paths"]["/downloads/{filename}"]["get"]
    assert download["parameters"][0]["description"] == "Name of the PDF file to download"
    not_found = download["responses"]["404"]["content"]["application/json"]
    assert not_found["example"]["code"] == "file_not_found"

    error_props = schema["components"]["schemas"]["ErrorResponse"]["properties"]
    assert set(error_props.keys()) == {"status", "code", "message", "details"}
