from fastapi.testclient import TestClient
from app.main import app
from app import database


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "customer-requests"


def test_startup_creates_database(tmp_path, monkeypatch):
    fresh_path = tmp_path / "fresh-startup.db"
    monkeypatch.setattr(database, "DATABASE_PATH", fresh_path)
    assert not fresh_path.exists()

    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Startup test"},
        )

    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert fresh_path.exists()
