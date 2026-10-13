from fastapi.testclient import TestClient
from app.main import app
import pytest


def test_valid_request():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={
                "customer_name": "Karim",
                "message": "Are office chairs available?",
            },
        )

    assert response.status_code == 201
    assert response.json()["status"] == "received"
    assert response.json()["customer_name"] == "Karim"
    assert response.json()["message"] == "Are office chairs available?"
    assert response.json()["id"] > 0

def test_missing_message():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={"customer_name": "Karim"},
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "message"]

def test_empty_message():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": ""},
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "message"]


def test_spaces_only_message():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "   "},
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "message"]

@pytest.mark.parametrize(
    "field,value,expected_status",
    [
        ("customer_name", "", 422),
        ("customer_name", "   ", 422),
        ("customer_name", "K", 201),
        ("customer_name", "K" * 100, 201),
        ("customer_name", "K" * 101, 422),
        ("message", "x", 201),
        ("message", "x" * 2000, 201),
        ("message", "x" * 2001, 422),
    ],
)
def test_input_boundaries(field, value, expected_status):
    payload = {"customer_name": "Karim", "message": "Office chairs available?"}
    payload[field] = value

    with TestClient(app) as client:
        response = client.post("/requests", json=payload)

    assert response.status_code == expected_status
    if expected_status == 422:
        assert response.json()["detail"][0]["loc"] == ["body", field]


def test_edge_spaces_are_trimmed():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={
                "customer_name": "  Karim  ",
                "message": "  Office chairs available?  ",
            },
        )

    assert response.status_code == 201
    assert response.json()["customer_name"] == "Karim"
    assert response.json()["message"] == "Office chairs available?"


def test_get_saved_request():
    with TestClient(app) as client:
        created = client.post(
            "/requests",
            json={
                "customer_name": "Karim",
                "message": "Are office chairs available?",
            },
        )
        assert created.status_code == 201
        request_id = created.json()["id"]
        response = client.get(f"/requests/{request_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": request_id,
        "customer_name": "Karim",
        "message": "Are office chairs available?",
    }


def test_get_missing_request():
    with TestClient(app) as client:
        response = client.get("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"


def test_get_invalid_id():
    with TestClient(app) as client:
        response = client.get("/requests/abc")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "request_id"]

from fastapi.testclient import TestClient
from app.main import app
