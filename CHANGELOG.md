# Changelog

All notable changes to this project will be documented in this file.
See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [Unreleased]
### Added
- `CreatePDFResponse` model and request field examples.
- Secured API key handling and enriched route metadata.
- OpenAPI specification saved as `openapi.json` in the project root.
- Initial test suite covering API key validation, PDF creation endpoint, and downloads cleanup.
- Expanded tests for PDF generation helper, request model validation, authentication edge cases, cleanup errors, and route handling.
- `ErrorResponse` model for consistent error payloads.
- Download endpoint for serving generated PDFs.
- Custom OpenAPI generator with HTTP Bearer auth metadata and URI format for PDF URLs.
- Expanded `ErrorResponse` fields and documented examples across endpoints.
- Added descriptive download endpoint route and comprehensive OpenAPI metadata including server URLs.
### Changed
- Added strict validation for `CreatePDFRequest` fields including title length, content sanitization, CSS restrictions, and normalized output filenames.
