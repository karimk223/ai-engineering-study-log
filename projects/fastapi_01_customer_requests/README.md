# Customer Requests API

A FastAPI application that creates, retrieves, updates, deletes and lists customer requests in SQLite, with input validation, pagination and automated persistence tests.

## Setup and run

Use Python 3.12 with SQLite 3.35 or later. From this project's directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [Swagger documentation](http://127.0.0.1:8000/docs) or [health](http://127.0.0.1:8000/health). Ctrl+C stops the server. Reload mode is for local development.

Requirements use the versions recorded in requirements.lock.txt, including Pydantic 1.10.26. The suite passes 51 cases on Python 3.12.13/macOS with SQLite 3.53.0, including verification in a fresh dependency installation. The snapshot pins versions without artifact hashes or a guarantee for all platforms.

Startup creates customer_requests.db and its table if absent. Existing records in that file remain across normal restarts.

## API

| Method | Path | Result |
| --- | --- | --- |
| GET | /health | 200: service response |
| POST | /requests | 201: saves a request and returns its ID |
| GET | /requests/{request_id} | 200: retrieves one request |
| PUT | /requests/{request_id} | 200: replaces both fields of an existing request |
| DELETE | /requests/{request_id} | 200: deletion receipt |
| GET | /requests?limit=10&offset=0 | 200: ordered page of requests |

POST and PUT accept:

```json
{
  "customer_name": "Demo Customer",
  "message": "Please send a quote for office chairs."
}
```

Both fields must be strings. Surrounding whitespace is trimmed before checking lengths: name 1–100, message 1–2000 characters. Unsupported fields are rejected. Invalid input gives 422; a valid ID with no record gives 404. Path IDs must be 1–9,223,372,036,854,775,807.

Use the returned ID for retrieval/update/deletion. PUT requires both fields and does not create an absent record. DELETE removes the row permanently. POST's status: received is a receipt rather than a stored field.

Listing defaults to limit 10 and offset 0. Limit accepts 1–100; offset accepts 0–1,000,000 and skips existing rows. Empty pages return 200 with items: [].

## Tests and notes

Run python -m pytest -q from this directory with the environment activated. Tests use temporary databases and do not require a live server. They check startup, validation, CRUD, pagination and persistence across application lifecycle contexts. Invalid-body tests also check that stored records remain unchanged.

The existing Starlette/AnyIO deprecation warning does not fail the suite. Lifecycle contexts run in one process; a manual server restart was checked separately. These tests cover selected scenarios.

[Notes](NOTES.md) explain the main concepts. This local application has no AI model, authentication or cloud deployment. Health only confirms the service responds. Environments, local databases and caches are excluded from Git.
