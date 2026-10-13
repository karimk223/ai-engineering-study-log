import pytest
from fastapi.testclient import TestClient

from app.main import SQLITE_MAX_INTEGER, app


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
@pytest.mark.parametrize(
    "request_id",
    [0, -1, SQLITE_MAX_INTEGER + 1],
)
def test_invalid_request_ids_are_rejected(method, request_id):
    arguments = {}

    if method == "PUT":
        arguments["json"] = {
            "customer_name": "Karim",
            "message": "Updated message",
        }

    with TestClient(app) as client:
        response = client.request(
            method,
            f"/requests/{request_id}",
            **arguments,
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == [
        "path",
        "request_id",
    ]


def test_largest_sqlite_id_is_accepted():
    with TestClient(app) as client:
        response = client.get(
            f"/requests/{SQLITE_MAX_INTEGER}"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"
