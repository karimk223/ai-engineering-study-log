import json
from pathlib import Path

from dotenv import dotenv_values
from groq import Groq

from tools import MULTIPLY_TOOL, multiply


def main():
    api_project = Path(__file__).resolve().parents[1] / "fastapi_03_llm_tools_api"
    api_key = dotenv_values(api_project / ".env").get("GROQ_API_KEY")

    if not api_key or not api_key.strip():
        raise RuntimeError("GROQ_API_KEY is missing from the existing API project.")

    messages = [
        {
            "role": "system",
            "content": (
             "Use multiply for multiplication. Request one tool at a time."
             "Answer in plain text. Do not use LaTeX or Markdown formatting."
            ),
        },
        {
            "role": "user",
            "content": "There are 18 boxes with 24 items each. How many items in total?",
        },
    ]

    with Groq(api_key=api_key.strip(), timeout=20.0, max_retries=0) as client:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=[MULTIPLY_TOOL],
            tool_choice="auto",
            parallel_tool_calls=False,
            reasoning_effort="low",
            include_reasoning=False,
            max_completion_tokens=1024,
        )

    choice = response.choices[0]
    calls = choice.message.tool_calls or []

    if choice.finish_reason != "tool_calls" or len(calls) != 1:
        raise RuntimeError("Expected one complete tool request.")

    call = calls[0]
    if call.type != "function" or call.function.name != "multiply":
        raise RuntimeError("The model requested an unavailable tool.")

    arguments = json.loads(call.function.arguments)
    if not isinstance(arguments, dict) or set(arguments) != {"a", "b"}:
        raise ValueError("The tool needs exactly two inputs: a and b.")

    print("Requested tool:", call.function.name)
    print("Requested inputs:", arguments)

    input("Press Enter to run this tool...")
    result = multiply(arguments["a"], arguments["b"])
    print("Tool result:", result)

    messages.append(
        choice.message.model_dump(
            include={"role", "content", "tool_calls"}, exclude_none=True
        )
    )
    messages.append(
        {
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result),
        }
    )

    with Groq(api_key=api_key.strip(), timeout=20.0, max_retries=0) as client:
        final_response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=[MULTIPLY_TOOL],
            tool_choice="none",
            parallel_tool_calls=False,
            reasoning_effort="low",
            include_reasoning=False,
            max_completion_tokens=1024,
        )

    final_choice = final_response.choices[0]
    answer = final_choice.message.content

    if (
        final_choice.finish_reason != "stop"
        or final_choice.message.tool_calls
        or not answer
        or not answer.strip()
    ):
        raise RuntimeError("The model did not return a complete final answer.")

    print("Final answer:", answer.strip())


if __name__ == "__main__":
    main()