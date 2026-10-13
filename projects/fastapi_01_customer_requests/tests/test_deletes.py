from fastapi.testclient import TestClient
from app.main import app


def test_delete_saved_request_keeps_other_record():
    with TestClient(app) as client:
        created = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Delete this request"},
        )
        other = client.post(
            "/requests",
            json={"customer_name": "Nour", "message": "Keep this request"},
        )
        assert created.status_code == 201
        assert other.status_code == 201
        request_id = created.json()["id"]
        other_id = other.json()["id"]

        before_other = client.get(f"/requests/{other_id}")
        assert before_other.status_code == 200

        deleted = client.delete(f"/requests/{request_id}")
        after = client.get(f"/requests/{request_id}")
        still_there = client.get(f"/requests/{other_id}")
        deleted_again = client.delete(f"/requests/{request_id}")

    assert deleted.status_code == 200
    assert deleted.json() == {"status": "deleted", "id": request_id}
    assert after.status_code == 404
    assert after.json()["detail"] == "Request not found"
    assert still_there.status_code == 200
    assert still_there.json() == before_other.json()
    assert deleted_again.status_code == 404
    assert deleted_again.json()["detail"] == "Request not found"


def test_delete_missing_request():
    with TestClient(app) as client:
        response = client.delete("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"


def test_delete_invalid_id():
    with TestClient(app) as client:
        response = client.delete("/requests/abc")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "request_id"]
