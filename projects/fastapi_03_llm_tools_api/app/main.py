from contextlib import asynccontextmanager
from pathlib import Path

import json
import groq
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, Path as ApiPath
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from app.tools import ORDER_STATUS_TOOL, OrderStatusArgs, get_order_status
from app.database import init_database, save_chat, get_chat


MODEL = "openai/gpt-oss-120b"


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = dotenv_values(Path(__file__).resolve().parent.parent / ".env")
    api_key = config.get("GROQ_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError("GROQ_API_KEY is missing from .env.")

    with groq.Groq(api_key=api_key.strip(), timeout=20.0, max_retries=0) as client:
        app.state.llm_client = client
        init_database()
        yield


app = FastAPI(title="LLM Tools API", lifespan=lifespan)


class ChatInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(strict=True, min_length=1, max_length=2000)

class LLMReply(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    reply: str = Field(strict=True, min_length=1)

class ChatOutput(BaseModel):
    id: int
    reply: str
    model: str
    tool_used: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


def call_llm(messages: list[dict], tool_choice: str = "auto"):
    try:
        response = app.state.llm_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[ORDER_STATUS_TOOL],
            tool_choice=tool_choice,
            parallel_tool_calls=False,
            reasoning_effort="medium",
            include_reasoning=False,
            max_completion_tokens=1024,
        )
    except groq.APITimeoutError as exc:
        raise HTTPException(status_code=504, detail="LLM request timed out") from exc
    except groq.RateLimitError as exc:
        raise HTTPException(
            status_code=503, detail="LLM rate limit reached. Try again later."
        ) from exc
    except groq.APIError as exc:
        raise HTTPException(status_code=502, detail="LLM provider request failed") from exc

    if not response.choices:
        raise HTTPException(status_code=502, detail="LLM returned no reply")

    return response


@app.post("/chat", response_model=ChatOutput)
def chat(payload: ChatInput):
    messages = [
        {
            "role": "system",
            "content": (
                "You assist a fictional trading company. Answer briefly. "
                "For order status, use get_order_status with the exact ID the user gave. "
                "Never invent an order ID or status. If no ID is given, ask for it. "
                "You may look up only one order per message; ask the user to choose "
                "one if several are requested. If found is false, say the order "
                "was not found. You cannot change orders or issue refunds."
                "For your final answer, return only a JSON object with exactly "
                "one field: "
                '{"reply": "your answer"}. '
                "Do not include Markdown fences around the JSON."
            ),
        },
        {"role": "user", "content": payload.message},
    ]

    tool_used = None
    tool_record = None
    response = call_llm(messages)
    choice = response.choices[0]
    message = choice.message

    if message.tool_calls:
        if choice.finish_reason != "tool_calls" or len(message.tool_calls) != 1:
            raise HTTPException(status_code=502, detail="Invalid tool-call response")

        call = message.tool_calls[0]
        if (
            call.type != "function"
            or call.function.name != "get_order_status"
            or not call.id
        ):
            raise HTTPException(status_code=502, detail="Tool call not allowed")

        try:
            args = OrderStatusArgs.model_validate_json(
                call.function.arguments, strict=True
            )
        except ValidationError as exc:
            raise HTTPException(
                status_code=502, detail="LLM supplied invalid tool arguments"
            ) from exc

        result = get_order_status(args.order_id)
        tool_used = "get_order_status"
        tool_record = {
            "tool_call_id": call.id,
            "tool_name": tool_used,
            "arguments": args.model_dump(),
            "result": result,
        }

        messages.append(
            message.model_dump(
                include={"role", "content", "tool_calls"}, exclude_none=True
            )
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            }
        )

        response = call_llm(messages, tool_choice="none")
        choice = response.choices[0]

    answer = choice.message.content
    if (
        choice.message.tool_calls
        or choice.finish_reason != "stop"
        or not answer
        or not answer.strip()
    ):
        raise HTTPException(status_code=502, detail="LLM returned an incomplete reply")

    try:
        final_reply = LLMReply.model_validate_json(
            answer, strict=True
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid reply format",
        ) from exc

    chat_id = save_chat(
        payload.message,
        final_reply.reply,
        response.model,
        tool_record,
    )

    return ChatOutput(
        id=chat_id,
        reply=final_reply.reply,
        model=response.model,
        tool_used=tool_used,
    )

@app.get("/chats/{chat_id}")
def read_chat(
    chat_id: int = ApiPath(ge=1, le=9_223_372_036_854_775_807),
):
    record = get_chat(chat_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return record