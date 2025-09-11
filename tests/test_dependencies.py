import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

import app.config as config
from app.dependencies import cleanup_downloads_folder, get_api_key


def test_get_api_key_valid(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    result = get_api_key("secret")
    assert result == "secret"


def test_get_api_key_invalid(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", "secret")
    with pytest.raises(HTTPException) as exc:
        get_api_key("wrong")
    assert exc.value.status_code == 403


def test_get_api_key_no_env(monkeypatch):
    monkeypatch.setattr(config.settings, "API_KEY", None)
    result = get_api_key("provided")
    assert result == "provided"


@pytest.mark.asyncio
async def test_cleanup_downloads_folder(tmp_path):
    old_file = tmp_path / "old.txt"
    old_file.write_text("old")
    old_time = datetime.now(tz=timezone.utc) - timedelta(days=8)
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
