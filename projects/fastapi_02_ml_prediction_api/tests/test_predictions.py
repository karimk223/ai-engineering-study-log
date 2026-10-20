import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


def test_startup_and_health(client, isolated_database):
    response = client.get("/health")

    assert isolated_database.exists()
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_version"] == "ticket-router-full-v1"


def test_predict_and_read_saved_record(client):
    message = "Please unsubscribe me from your newsletter."
    response = client.post("/predict", json={"message": f"  {message}  "})

    assert response.status_code == 200
    result = response.json()
    assert result["id"] > 0
    assert result["category"] == "SUBSCRIPTION"
    assert 0 <= result["score"] <= 1
    assert result["model_version"] == "ticket-router-full-v1"

    saved_response = client.get(f"/predictions/{result['id']}")
    assert saved_response.status_code == 200
    record = saved_response.json()

    assert record["message"] == message
    assert record["created_at"]
    for field in ["id", "category", "score", "model_version"]:
        assert record[field] == result[field]

    with closing(sqlite3.connect(database.DATABASE_PATH)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    assert count == 1


def test_missing_prediction(client):
    response = client.get("/predictions/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Prediction not found"}


@pytest.mark.parametrize("payload", [
    {},
    {"message": ""},
    {"message": "   "},
    {"message": 123},
    {"message": None},
    {"message": "x" * 2001},
    {"message": "Hello", "extra": True},
])
def test_invalid_body_is_not_saved(client, payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    with closing(sqlite3.connect(database.DATABASE_PATH)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    assert count == 0


@pytest.mark.parametrize("prediction_id", [
    0,
    -1,
    "abc",
    "1.5",
    9_223_372_036_854_775_808,
])
def test_invalid_prediction_id(client, prediction_id):
    response = client.get(f"/predictions/{prediction_id}")
    assert response.status_code == 422


def test_prediction_survives_restart():
    with TestClient(app) as first_client:
        created = first_client.post(
            "/predict",
            json={"message": "Please unsubscribe me from your newsletter."},
        )
        assert created.status_code == 200
        result = created.json()
        saved = first_client.get(f"/predictions/{result['id']}")
        assert saved.status_code == 200
        record = saved.json()

    with TestClient(app) as second_client:
        restored = second_client.get(f"/predictions/{result['id']}")

    assert restored.status_code == 200
    assert restored.json() == record