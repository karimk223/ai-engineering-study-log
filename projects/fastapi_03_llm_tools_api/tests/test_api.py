import json
import pytest

from unittest.mock import Mock
from groq.types.chat import ChatCompletion
from app.main import MODEL
from app import main

import sqlite3
from contextlib import closing

import groq
import httpx

from app import database

def completion(content):
    return ChatCompletion.model_validate({
        "id": "test-response",
        "created": 0,
        "object": "chat.completion",
        "model": MODEL,
        "choices": [{
            "index": 0,
            "finish_reason": "stop",
            "message": {"role": "assistant", "content": content},
        }],
    })


def test_health(api):
    client, llm = api

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": MODEL}
    llm.chat.completions.create.assert_not_called()


def test_chat_saved_and_retrieved(api):
    client, llm = api
    llm.chat.completions.create.side_effect = [
        completion('{"reply": "  Hello!  "}')
    ]

    response = client.post("/chat", json={"message": "  Hi  "})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "reply": "Hello!",
        "model": MODEL,
        "tool_used": None,
    }

    saved = client.get("/chats/1")
    assert saved.status_code == 200
    assert saved.json()["user_message"] == "Hi"
    assert saved.json()["assistant_reply"] == "Hello!"
    assert saved.json()["tool_calls"] == []
    assert saved.json()["created_at"]
    llm.chat.completions.create.assert_called_once()


@pytest.mark.parametrize("body", [
    {},
    {"message": ""},
    {"message": "   "},
    {"message": 42},
    {"message": True},
    {"message": None},
    {"message": "x" * 2001},
    {"message": "Hi", "extra": True},
])
def test_invalid_input(api, body):
    client, llm = api

    assert client.post("/chat", json=body).status_code == 422
    assert client.get("/chats/1").status_code == 404
    llm.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("content", [
    "Plain text instead of JSON",
    "{}",
    '{"reply": 42}',
    '{"reply": "   "}',
    '{"reply": "Hello!", "extra": true}',
])
def test_invalid_ai_reply_not_saved(api, content):
    client, llm = api
    llm.chat.completions.create.side_effect = [completion(content)]

    response = client.post("/chat", json={"message": "Hi"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "LLM returned an invalid reply format"
    }
    assert client.get("/chats/1").status_code == 404
    llm.chat.completions.create.assert_called_once()

def tool_completion(arguments, name="get_order_status"):
    response = completion(None).model_dump()
    choice = response["choices"][0]
    choice["finish_reason"] = "tool_calls"
    choice["message"]["tool_calls"] = [{
        "id": "call-test",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }]
    return ChatCompletion.model_validate(response)


@pytest.mark.parametrize("order_id, status, reply", [
    (102, "shipped", "Order 102 is shipped."),
    (999, None, "Order 999 was not found."),
])
def test_order_lookup_saved(api, order_id, status, reply):
    client, llm = api
    create = llm.chat.completions.create
    create.side_effect = [
        tool_completion(json.dumps({"order_id": order_id})),
        completion(json.dumps({"reply": reply})),
    ]

    response = client.post(
        "/chat", json={"message": f"Status of order {order_id}?"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "reply": reply,
        "model": MODEL,
        "tool_used": "get_order_status",
    }

    expected_result = {
        "order_id": order_id,
        "found": status is not None,
        "status": status,
    }

    saved = client.get("/chats/1")
    assert saved.status_code == 200
    record = saved.json()
    assert record["assistant_reply"] == reply
    assert len(record["tool_calls"]) == 1

    tool_log = record["tool_calls"][0]
    assert tool_log["tool_call_id"] == "call-test"
    assert tool_log["tool_name"] == "get_order_status"
    assert tool_log["arguments"] == {"order_id": order_id}
    assert tool_log["result"] == expected_result

    assert create.call_count == 2
    first, second = create.call_args_list
    assert first.kwargs["tool_choice"] == "auto"
    assert second.kwargs["tool_choice"] == "none"

    tool_message = second.kwargs["messages"][-1]
    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call-test"
    assert json.loads(tool_message["content"]) == expected_result


@pytest.mark.parametrize("arguments", [
    "not-json",
    "{}",
    '{"order_id": "102"}',
    '{"order_id": 0}',
    '{"order_id": 102, "extra": true}',
    '{"order_id": 9223372036854775808}',
])
def test_bad_tool_arguments_rejected(api, monkeypatch, arguments):
    client, llm = api
    lookup = Mock()
    monkeypatch.setattr(main, "get_order_status", lookup)
    llm.chat.completions.create.side_effect = [
        tool_completion(arguments)
    ]

    response = client.post("/chat", json={"message": "Order 102?"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "LLM supplied invalid tool arguments"
    }
    lookup.assert_not_called()
    assert client.get("/chats/1").status_code == 404
    llm.chat.completions.create.assert_called_once()


def test_unapproved_tool_rejected(api, monkeypatch):
    client, llm = api
    lookup = Mock()
    monkeypatch.setattr(main, "get_order_status", lookup)
    llm.chat.completions.create.side_effect = [
        tool_completion('{"order_id": 102}', name="delete_order")
    ]

    response = client.post("/chat", json={"message": "Order 102?"})

    assert response.status_code == 502
    assert response.json() == {"detail": "Tool call not allowed"}
    lookup.assert_not_called()
    assert client.get("/chats/1").status_code == 404
    llm.chat.completions.create.assert_called_once()

def assert_no_logs():
    queries = (
        "SELECT COUNT(*) FROM conversations",
        "SELECT COUNT(*) FROM tool_calls",
    )
    with closing(sqlite3.connect(database.DATABASE_PATH)) as connection:
        for query in queries:
            assert connection.execute(query).fetchone()[0] == 0


@pytest.mark.parametrize("after_tool", [False, True])
@pytest.mark.parametrize("kind, status, detail", [
    ("timeout", 504, "LLM request timed out"),
    ("rate_limit", 503, "LLM rate limit reached. Try again later."),
    ("connection", 502, "LLM provider request failed"),
])
def test_provider_failure(api, after_tool, kind, status, detail):
    client, llm = api
    request = httpx.Request("POST", "https://example.test/chat")

    if kind == "timeout":
        error = groq.APITimeoutError(request=request)
    elif kind == "rate_limit":
        error = groq.RateLimitError(
            "Private provider details",
            response=httpx.Response(429, request=request),
            body=None,
        )
    else:
        error = groq.APIConnectionError(request=request)

    replies = [error]
    if after_tool:
        replies.insert(0, tool_completion('{"order_id": 102}'))
    llm.chat.completions.create.side_effect = replies

    response = client.post("/chat", json={"message": "Order 102?"})

    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert llm.chat.completions.create.call_count == (2 if after_tool else 1)
    assert_no_logs()


@pytest.mark.parametrize("kind", [
    "empty", "blank", "truncated", "no_choices", "extra_tool",
])
def test_bad_final_response_after_tool(api, monkeypatch, kind):
    client, llm = api
    lookup = Mock(wraps=main.get_order_status)
    monkeypatch.setattr(main, "get_order_status", lookup)

    bad = completion('{"reply": "Order 102 is shipped."}')
    detail = "LLM returned an incomplete reply"

    if kind == "empty":
        bad.choices[0].message.content = None
    elif kind == "blank":
        bad.choices[0].message.content = "   "
    elif kind == "truncated":
        bad.choices[0].finish_reason = "length"
    elif kind == "no_choices":
        bad.choices = []
        detail = "LLM returned no reply"
    else:
        bad = tool_completion('{"order_id": 103}')

    llm.chat.completions.create.side_effect = [
        tool_completion('{"order_id": 102}'),
        bad,
    ]

    response = client.post("/chat", json={"message": "Order 102?"})

    assert response.status_code == 502
    assert response.json() == {"detail": detail}
    assert llm.chat.completions.create.call_count == 2
    lookup.assert_called_once_with(102)
    assert_no_logs()


@pytest.mark.parametrize("chat_id", [
    "0", "-1", "abc", "9223372036854775808",
])
def test_invalid_chat_id(api, chat_id):
    client, llm = api

    assert client.get(f"/chats/{chat_id}").status_code == 422
    llm.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("chat_id", [999, 9_223_372_036_854_775_807])
def test_missing_chat(api, chat_id):
    client, llm = api

    response = client.get(f"/chats/{chat_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}
    llm.chat.completions.create.assert_not_called()


def test_database_initialization_preserves_chat(api):
    client, llm = api
    chat_id = database.save_chat("Where's my order?", "Saved reply", MODEL)
    before = database.get_chat(chat_id)

    database.init_database()

    assert database.get_chat(chat_id) == before
    assert client.get(f"/chats/{chat_id}").json() == before
    llm.chat.completions.create.assert_not_called()


def test_failed_tool_save_rolls_back_chat(api):
    with pytest.raises(sqlite3.IntegrityError):
        database.save_chat("Hi", "Hello!", MODEL, {
            "tool_call_id": "call-test",
            "tool_name": None,
            "arguments": {},
            "result": {},
        })

    assert_no_logs()