# Customer Requests API — compact notes

- API: programs exchange requests and responses. FastAPI connects a method/URL to a Python function. JSON carries the data.
- POST creates (201); GET reads (200); PUT replaces both fields of an existing record (200); DELETE removes it (200). Valid but absent ID: 404. Invalid body/path/query: 422.
- CustomerRequest checks real strings, allowed fields, trimming and lengths before a handler runs. The shared RequestId annotation checks the positive SQLite integer range.
- POST flow: JSON -> validated model -> receive_request -> save_request -> INSERT/commit -> returned ID -> JSON receipt. SQLite holds the saved data; the response itself is not storage.
- Database helpers use parameterized SQL with ? placeholders. WHERE id = ? selects one record. commit persists a write; closing closes the connection. UPDATE RETURNING returns the changed row. DELETE rowcount indicates whether a row was removed.
- Lifespan runs init_database at startup. CREATE TABLE IF NOT EXISTS preserves an existing table; a missing file creates new empty storage. It neither recovers lost files nor migrates schemas.
- Listing uses ORDER BY id, LIMIT and OFFSET. Limit caps the number returned; offset skips existing rows, independent of ID gaps. A/B/C/D with limit 2, offset 1 returns B/C.
- Pytest supplies inputs from JSON examples and parameter tables. Two parameter decorators produce combinations, not extra functions. A test passes when the observed response matches its expectation, including expected errors.
- The autouse fixture gives each case a temporary database. Multiple TestClient contexts within one case reuse that file and exercise application startup/shutdown.
- Invalid POSTs must create no record; invalid PUTs must leave stored data unchanged. Passing cases cover selected behavior, not all possible failures.
- Dependencies are installed Python packages. Version constraints reproduce the tested versions; a fresh environment checks that setup does not rely on unrecorded local packages.
- Implemented locally: FastAPI/SQLite CRUD and validation with 51 regression cases. AI models, authentication and cloud deployment belong to later work.
