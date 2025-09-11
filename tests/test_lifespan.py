from fastapi.testclient import TestClient
import app.main as main_module


def test_lifespan_runs_cleanup(monkeypatch):
    calls = []

    async def fake_cleanup(path):
        calls.append(path)

    monkeypatch.setattr(main_module, "cleanup_downloads_folder", fake_cleanup)

    with TestClient(main_module.app):
        pass

    assert calls == ["/app/downloads", "/app/downloads"]

