# API 3 — learning notes

## What is different from API 2?

API 2 fits a text classifier offline, saves a Joblib artifact and loads that trained pipeline in FastAPI. API 3 does not fit a model or load a local model file. It sends requests through the Groq SDK to a pretrained hosted model.

The API key authorizes provider access; it is not a model and does not teach the model anything.

## Who executes a tool?

The LLM proposes a native function call such as `get_order_status({"order_id": 102})`. Our Python application checks the function name and arguments, then executes the allowed Python function itself. The model does not directly run Python or access SQLite.

We append the actual lookup result as a tool message with the matching call ID, then ask the model for a final answer. At most one lookup and two model requests are allowed. A model reply saying it used a tool is not evidence; the server sets `tool_used` after executing the approved function.

## Why are there two kinds of JSON?

The client sends JSON to our API. Independently, the model's final message is text that we ask to contain `{"reply": "..."}`.

`LLMReply.model_validate_json` checks that text and produces a Python object. `LLMReply` is a Pydantic schema, not another AI model. Its `reply` must be a strict nonblank string, and extra fields are forbidden.

The API then returns `ChatOutput`, adding the saved chat ID, model name and server-generated tool name. Swagger can look the same before/after adding the internal model-format check because the API already returned JSON.

A well-formed answer can still be factually wrong. Format validation and answer quality are different checks.

## What does SQLite save?

One successful exchange creates a conversations row. A successful exchange that executed the order tool also creates one linked tool_calls row with its name, provider call ID, JSON arguments and actual JSON result.

Both inserts share one transaction. Either both are saved or neither is. A failed exchange is not logged by this small implementation.

The chat row ID identifies the saved exchange, not the order. Order 102 can appear in many chats, each with a different chat ID.

GET reads the saved record without asking the model again. Saving records is not the same as supplying chat history to the model; this API has no memory across POSTs.

## Why use fake AI replies in tests?

A controlled fake lets us ask: if the provider returns this reply, tool call or error, does our application handle it correctly? It avoids quota use and unpredictable wording.

The tests still run real FastAPI handlers and SQLite code. Successful order tests also execute the real Python lookup. Rejection tests use a mock to prove a lookup never ran, while extra-tool tests wrap the real function to prove it ran only once.

`conftest.py` supplies a new temporary database, dummy key reader and fake Groq client per API test. These replacements are undone afterward. The real key and demo database are not used.

The 56 passing cases are application regression tests, not a 56-question evaluation of the real model and not a production accuracy score.

## Boundaries to remember

- Orders are fictional and read-only: 101 processing, 102 shipped, 103 delivered.
- Unknown IDs return not-found data, not a guessed status.
- Strict tool argument checks, the function allowlist and bounded calls are enforced by Python.
- Asking for one exact order ID or a particular JSON format is a prompt instruction; it is not a guarantee of factual correctness.
- Provider errors return sanitized client-facing HTTP errors. No billing upgrade, new model download or model-training detour is required.
- This demo is localhost-only and has no authentication or user-level access control.

## Version records

`requirements.txt` lists direct dependencies using the constraints in `requirements.lock.txt`. The 25-version snapshot records the working installed environment, not package hashes or a universal platform-independent resolution. SQLite is in Python's standard library and is not a separate pip dependency.
