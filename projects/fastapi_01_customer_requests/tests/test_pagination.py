import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_list_empty_database():
    with TestClient(app) as client:
        response = client.get("/requests")

    assert response.status_code == 200
    assert response.json() == {"items": [], "limit": 10, "offset": 0}


def test_list_defaults_return_first_ten():
    created_ids = []
    with TestClient(app) as client:
        for number in range(11):
            created = client.post(
                "/requests",
                json={"customer_name": "Karim", "message": f"Request {number}"},
            )
            assert created.status_code == 201
            created_ids.append(created.json()["id"])

        response = client.get("/requests")

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 10
    assert [item["id"] for item in data["items"]] == created_ids[:10]


def test_list_pages_skip_rows_not_ids():
    created_ids = []
    with TestClient(app) as client:
        for name in ("Karim", "Nour", "Maya"):
            created = client.post(
                "/requests",
                json={"customer_name": name, "message": "Pagination test"},
            )
            assert created.status_code == 201
            created_ids.append(created.json()["id"])

        deleted = client.delete(f"/requests/{created_ids[1]}")
        assert deleted.status_code == 200

        first = client.get("/requests", params={"limit": 1, "offset": 0})
        second = client.get("/requests", params={"limit": 1, "offset": 1})
        beyond = client.get("/requests", params={"limit": 1, "offset": 2})

    assert first.status_code == 200
    assert second.status_code == 200
    assert [item["id"] for item in first.json()["items"]] == [created_ids[0]]
    assert [item["id"] for item in second.json()["items"]] == [created_ids[2]]
    assert first.json()["limit"] == second.json()["limit"] == 1
    assert first.json()["offset"] == 0
    assert second.json()["offset"] == 1
    assert beyond.status_code == 200
    assert beyond.json()["items"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("limit", 0),
        ("limit", 101),
        ("limit", "abc"),
        ("offset", -1),
        ("offset", 1_000_001),
        ("offset", "abc"),
    ],
)
def test_invalid_pagination(field, value):
    with TestClient(app) as client:
        response = client.get("/requests", params={field: value})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", field]
