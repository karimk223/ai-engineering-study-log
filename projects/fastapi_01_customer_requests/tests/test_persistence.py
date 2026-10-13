from fastapi.testclient import TestClient
from app.main import app


def test_request_survives_app_restart():
    with TestClient(app) as client:
        created = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Keep me after restart"},
        )
        assert created.status_code == 201
        request_id = created.json()["id"]

    with TestClient(app) as client:
        response = client.get(f"/requests/{request_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": request_id,
        "customer_name": "Karim",
        "message": "Keep me after restart",
    }


def test_update_and_delete_survive_app_restart():
    with TestClient(app) as client:
        first = client.post(
            "/requests",
            json={"customer_name": "Karim", "message": "Original message"},
        )
        second = client.post(
            "/requests",
            json={"customer_name": "Nour", "message": "Delete me"},
        )
        assert first.status_code == 201
        assert second.status_code == 201
        first_id = first.json()["id"]
        second_id = second.json()["id"]

    with TestClient(app) as client:
        updated = client.put(
            f"/requests/{first_id}",
            json={"customer_name": "Karim", "message": "Updated message"},
        )
        assert updated.status_code == 200
        deleted = client.delete(f"/requests/{second_id}")
        assert deleted.status_code == 200

    with TestClient(app) as client:
        saved = client.get(f"/requests/{first_id}")
        removed = client.get(f"/requests/{second_id}")

    assert saved.status_code == 200
    assert saved.json() == {
        "id": first_id,
        "customer_name": "Karim",
        "message": "Updated message",
    }
    assert removed.status_code == 404
    assert removed.json()["detail"] == "Request not found"
