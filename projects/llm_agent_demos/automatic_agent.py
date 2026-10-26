import json
from pathlib import Path

from dotenv import dotenv_values
from groq import Groq

from tools import MULTIPLY_TOOL, multiply

MAX_TOOL_CALLS = 3
TOOL_FUNCTIONS = {"multiply": multiply}


def run_agent(client, question):
    messages = [
        {
            "role": "system",
            "content": (
                "Use multiply for every multiplication, one tool call at a time. "
                "For multi-step tasks, use each tool result before the next step. "
                "After the calculations, answer in plain text without LaTeX or Markdown."
            ),
        },
        {"role": "user", "content": question},
    ]

    for tools_used in range(MAX_TOOL_CALLS + 1):
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
        message = choice.message
        calls = message.tool_calls or []

        if not calls:
            answer = message.content
            if choice.finish_reason != "stop" or not answer or not answer.strip():
                raise RuntimeError("The model did not return a complete final answer.")
            return answer.strip()

        if choice.finish_reason != "tool_calls" or len(calls) != 1:
            raise RuntimeError("Expected one complete tool request at a time.")

        if tools_used == MAX_TOOL_CALLS:
            raise RuntimeError("Stopped: the limit of 3 tool calls was reached.")

        call = calls[0]
        name = call.function.name
        if call.type != "function" or name not in TOOL_FUNCTIONS:
            raise RuntimeError("The model requested an unavailable tool.")

        arguments = json.loads(call.function.arguments)
        if not isinstance(arguments, dict) or set(arguments) != {"a", "b"}:
            raise ValueError("The tool needs exactly two inputs: a and b.")

        result = TOOL_FUNCTIONS[name](**arguments)
        print(
            f"Tool call {tools_used + 1}: "
            f"{name}({arguments['a']}, {arguments['b']}) -> {result}"
        )

        messages.append(
            message.model_dump(
                include={"role", "content", "tool_calls"}, exclude_none=True
            )
        )
        messages.append(
            {"role": "tool", "tool_call_id": call.id, "content": str(result)}
        )

    raise RuntimeError("No final answer was returned.")


def main():
    api_project = Path(__file__).resolve().parents[1] / "fastapi_03_llm_tools_api"
    api_key = dotenv_values(api_project / ".env").get("GROQ_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError("GROQ_API_KEY is missing from the existing API project.")

    question = (
        "There are 18 boxes with 24 items each. Each item costs 3 dollars. "
        "First use the tool to find the item count, then use it again "
        "to calculate the total cost."
    )

    with Groq(api_key=api_key.strip(), timeout=20.0, max_retries=0) as client:
        answer = run_agent(client, question)

    print("Final answer:", answer)


if __name__ == "__main__":
    main()