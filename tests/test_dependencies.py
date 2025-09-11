import os
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import cleanup_downloads_folder, get_api_key


@pytest.mark.asyncio
async def test_get_api_key_valid(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="secret",
    )
    result = await get_api_key(credentials)
    assert result == "secret"


@pytest.mark.asyncio
async def test_get_api_key_invalid(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="wrong",
    )
    with pytest.raises(HTTPException) as exc:
        await get_api_key(credentials)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_api_key_no_env(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="provided",
    )
    result = await get_api_key(credentials)
    assert result == "provided"


@pytest.mark.asyncio
async def test_cleanup_downloads_folder(tmp_path):
    old_file = tmp_path / "old.txt"
    old_file.write_text("old")
    old_time = datetime.now() - timedelta(days=8)
    os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

    new_file = tmp_path / "new.txt"
    new_file.write_text("new")

    await cleanup_downloads_folder(str(tmp_path))

    assert not old_file.exists()
    assert new_file.exists()


@pytest.mark.asyncio
async def test_cleanup_downloads_folder_error(monkeypatch, tmp_path):
    def fail_listdir(path):
        raise OSError("boom")

    monkeypatch.setattr(os, "listdir", fail_listdir)
    with pytest.raises(HTTPException) as exc:
        await cleanup_downloads_folder(str(tmp_path))
    assert exc.value.status_code == 500
