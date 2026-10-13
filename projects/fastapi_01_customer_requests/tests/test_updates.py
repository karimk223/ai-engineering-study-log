from fastapi.testclient import TestClient
from app.main import app


def test_update_saved_request():
    with TestClient(app) as client:
        created = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Office chairs available?"},
        )
        assert created.status_code == 201
        request_id = created.json()["id"]

        new_data = {
            "customer_name": "Nour",
            "message": "Please send a quote for 10 chairs.",
        }
        updated = client.put(f"/requests/{request_id}", json=new_data)
        retrieved = client.get(f"/requests/{request_id}")

    expected = {
        "id": request_id,
        "customer_name": "Nour",
        "message": "Please send a quote for 10 chairs.",
    }
    assert updated.status_code == 200
    assert updated.json() == expected
    assert retrieved.status_code == 200
    assert retrieved.json() == expected


def test_update_missing_request():
    with TestClient(app) as client:
        response = client.put(
            "/requests/999999",
            json={"customer_name": "Karim", "message": "Updated message"},
        )
        retrieved = client.get("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"
    assert retrieved.status_code == 404


def test_invalid_update_keeps_saved_request():
    with TestClient(app) as client:
        created = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Original message"},
        )
        assert created.status_code == 201
        request_id = created.json()["id"]

        before = client.get(f"/requests/{request_id}")
        assert before.status_code == 200

        response = client.put(
            f"/requests/{request_id}",
            json={"customer_name": "Nour", "message": "   "},
        )
        after = client.get(f"/requests/{request_id}")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "message"]
    assert after.status_code == 200
    assert after.json() == before.json()
