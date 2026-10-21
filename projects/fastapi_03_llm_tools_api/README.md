# LLM Tools API

A guided-practice FastAPI application that uses Groq-hosted `openai/gpt-oss-120b` for short replies and a controlled, read-only fictional order lookup. This project uses a pretrained hosted model; it does not train or download a local LLM.

## What is implemented

- `GET /health`: local application status and configured model name; no inference.
- `POST /chat`: strict message validation, native tool calling when requested, validated final JSON and SQLite logging.
- `GET /chats/{chat_id}`: retrieve a saved exchange and its tool trace without another model call.
- One allowed function, `get_order_status`, with strict positive signed-64-bit integer arguments.
- At most one lookup and two model requests per chat; no arbitrary code execution or unbounded agent loop.
- 56 automated cases using a fake Groq client and isolated temporary databases.

The fictional orders are 101 = processing, 102 = shipped and 103 = delivered. Unknown IDs return `found: false` and `status: null`. No real customer, payment or order system is connected.

## Setup

Run commands from this project's directory, not the repository root. Keep each study-log project's environment separate: this application uses Pydantic 2.

For a new checkout, use Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m pip check
```

If this project already has its working `.venv`, activate it instead of recreating it.

`requirements.txt` lists the direct application/test dependencies and constrains them with `requirements.lock.txt`. The latter records all 25 installed dependency versions, excluding pip. Despite its filename, it is a [pip freeze version snapshot](https://pip.pypa.io/en/stable/cli/pip_freeze/), not a hash-verified or cross-platform lockfile. The verified interpreter is Python 3.12.13.

### Local credentials

For live use, create a local `.env` from `.env.example` only if `.env` does not already exist. Fill in `GROQ_API_KEY` privately in your editor. Preserve an existing configured file; do not overwrite it or paste its contents into logs, screenshots or Git.

Use your own Groq credential. This application calls Groq with the Groq SDK; it does not require an OpenAI API key. Keep the project's free-plan approach; no billing upgrade or local model download is part of setup. Live requests are subject to the account's current model availability and limits.

The application reads `.env` at startup and refuses to start with a missing or blank key. It does not verify the key with a live request at startup. The health endpoint does not establish provider connectivity.

### Tests without a key

```bash
python -m pytest -q
```

Expected: **56 passed**. Tests substitute a dummy credential reader and fake Groq client before startup, and redirect SQLite to temporary files. They do not read the real `.env`, call the provider or modify an existing `chats.db`. No running Uvicorn server is needed.

The verified Starlette/AnyIO versions emit one `BlockingPortal` deprecation warning. It is distinct from a failed test; the warning is not hidden by the suite.

### Start the local API

After configuring the private key:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

Open [Swagger UI](http://127.0.0.1:8002/docs).

`check_llm.py` is an optional standalone **live** connection check. Running it or sending a chat uses the provider and its quota; it is not an offline test. Do not import it into the application or test suite.

## Try it

In Swagger, send `POST /chat` with:

```json
{
  "message": "What is the status of order 102?"
}
```

An example response shape is:

```json
{
  "id": 1,
  "reply": "Order 102 is shipped.",
  "model": "openai/gpt-oss-120b",
  "tool_used": "get_order_status"
}
```

The exact wording and new chat ID can differ. Query `GET /chats/{chat_id}` using the returned ID. The saved chat ID is not the fictional order ID: chat 1 may describe order 102.

The GET result includes `id`, `user_message`, `assistant_reply`, `model`, `created_at` and a `tool_calls` list. Each tool entry includes its row ID, provider tool-call ID, function name, decoded arguments/result and creation time. A greeting normally has no tool trace. An unknown order can still be a successful lookup and therefore be logged.

## How a chat works

1. Validate and trim the incoming `message`: strict string, 1–2000 characters after trimming, no extra fields.
2. Ask the hosted model for an answer or a native tool request.
3. Before executing a tool, require the allowed function name, exactly one call, a nonempty call ID and valid JSON arguments. The lookup returns not-found data for an unknown ID.
4. Execute the Python lookup and send its actual result back with the matching `tool_call_id`. The second model request disables further tool calls.
5. Require a complete final response, then parse it with `LLMReply`. The expected model text is a JSON object with exactly one nonblank string field, `reply`.
6. Save the validated answer and optional tool trace in one SQLite transaction, then return the API's response object.

The API's `ChatOutput` JSON and the model's JSON text are separate layers. Final model formatting is prompt-guided and checked by Pydantic; this implementation does not use Groq's native schema-enforced `response_format`. Groq currently documents a [Structured Outputs/tool-use limitation](https://console.groq.com/docs/structured-outputs). Format validation is not proof that an answer's facts are correct.

The shared SDK client has a 20-second timeout per provider request and no automatic retries. An order exchange can make two requests; 20 seconds is not an overall end-to-end deadline.

## Storage and errors

On startup, `app/database.py` creates the ignored project-root `chats.db` if needed. The tables are `conversations` and `tool_calls`, linked by conversation ID. SQL values use placeholders. The parent chat and optional tool row commit together; a tool-row failure rolls back the chat insert.

Only completed successful exchanges are saved. Invalid input, provider failures and invalid/incomplete final responses produce no conversation or tool rows, even if the read-only lookup ran before a later failure. This is not a complete failure/audit log.

| Situation | HTTP result |
| --- | --- |
| Valid completed chat or existing saved chat | 200 |
| Invalid request body or chat ID | 422 |
| Missing valid chat ID | 404 |
| Provider timeout | 504 |
| Provider rate limit | 503 |
| Other SDK/provider error or invalid model/tool response | 502 |

Chat IDs are bounded to 1–9,223,372,036,854,775,807. SQLite creation timestamps use its UTC `CURRENT_TIMESTAMP` default.

## Verification and limits

Verified October 21, 2026: the saved local suite passes 56 cases and `pip check` reports no broken requirements. Tests cover successful chats/lookups, stored traces, strict input/tool/final-output validation, bounded tool execution, provider failures at either stage, invalid/missing IDs, database reinitialization and transaction rollback.

A clean source/configuration copy also passes all 56 cases using the existing verified interpreter and installed packages. That copy excludes the real `.env`, `chats.db`, environment and caches; imports were checked to resolve to the copied application. This verifies clean-file operation without a key, not a separate fresh dependency installation. All 25 recorded dependency versions match the installed snapshot.

Tests supply controlled model responses. They verify application behavior, not a real-model accuracy percentage. Earlier manual Groq/Swagger checks confirmed live connectivity and a real order-tool response; those calls are separate from the offline suite.

This is a localhost learning demo, not a production deployment. It has no authentication, ownership checks, public-service rate limiting or real order access. Do not expose it publicly or use sensitive customer data. Prompt instructions do not guarantee that the model always chooses the correct tool, order ID or wording. There is no conversation memory: each POST starts a fresh exchange; GET only reads saved records.

`.env`, `.venv`, caches and `*.db` are ignored by the repository. Only the blank credential template is intended for Git. Keep private credentials and generated databases out of commits.

See [learning notes](NOTES.md) and [Groq's model documentation](https://console.groq.com/docs/model/openai/gpt-oss-120b).
