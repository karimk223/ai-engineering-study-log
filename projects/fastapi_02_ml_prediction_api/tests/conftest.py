import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    test_path = tmp_path / "test_predictions.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_path)
    return test_path


@pytest.fixture
def client(isolated_database):
    with TestClient(app) as test_client:
        yield test_client