from pathlib import Path

from dotenv import dotenv_values
from groq import Groq

config = dotenv_values(Path(__file__).with_name(".env"))
api_key = config.get("GROQ_API_KEY")

if not api_key or not api_key.strip():
    raise RuntimeError("GROQ_API_KEY is missing from .env.")

with Groq(api_key=api_key.strip(), timeout=20.0, max_retries=0) as client:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Connection successful.",
            }
        ],
        reasoning_effort="low",
        include_reasoning=False,
        max_completion_tokens=256,
    )

choice = response.choices[0]
answer = choice.message.content

if choice.finish_reason != "stop" or not answer or not answer.strip():
    raise RuntimeError("The model did not return a complete text reply.")

print("Model:", response.model)
print("Reply:", answer.strip())