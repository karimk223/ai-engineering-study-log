# Study log

## October 12–13, 2026 — Customer Requests API

Implemented health and customer-request endpoints with FastAPI. SQLite stores accepted requests and returns an ID. GET, PUT and DELETE operate on that ID; listing orders records by ascending ID and supports limit/offset.

Validation requires the two supported text fields, trims surrounding spaces, checks lengths, and rejects invalid IDs. Incorrect bodies return 422 before a write. Missing valid IDs return 404.

Verified 51 regression cases in the original environment and in a fresh installation from recorded dependencies. Package versions match and pip check reports no broken requirements. Tests isolate data in temporary databases. Lifecycle checks cover creation, updates and deletion across repeated startup/shutdown; a manual server-restart check was completed earlier.

Learning notes cover request/response flow, validation before storage, persistence, HTTP status codes and row-based pagination. For example, A/B/C/D with limit 2 and offset 1 returns B/C.

The first project's code is grouped under projects/fastapi_01_customer_requests. A newly created environment in that directory independently passes 51 cases (one dependency deprecation warning), and pip check reports no broken requirements. The server starts from the grouped app, and VS Code shows the study-log collection. Original practice data and lesson history remain in the original folder. GitHub publication is pending.

## Next

Prepare the local Git commit and publish the first milestone, then build the ML ticket-routing API in this collection. The LLM/tools API follows. Ingestion/RAG/agents and Odoo remain separate future repositories.
