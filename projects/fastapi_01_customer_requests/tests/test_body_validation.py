import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("customer_name", 123),
        ("message", 123),
        ("priority", "urgent"),
    ],
)
def test_invalid_body_does_not_change_saved_data(method, field, value):
    original_body = {
        "customer_name": "Karim",
        "message": "Original message",
    }
    payload = {
        "customer_name": "Karim",
        "message": "Replacement message",
    }
    payload[field] = value

    with TestClient(app) as client:
        created = client.post("/requests", json=original_body)
        assert created.status_code == 201
        request_id = created.json()["id"]

        url = (
            "/requests"
            if method == "POST"
            else f"/requests/{request_id}"
        )
        response = client.request(method, url, json=payload)

        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", field]

        saved_records = client.get("/requests").json()["items"]
        assert saved_records == [{"id": request_id, **original_body}]
