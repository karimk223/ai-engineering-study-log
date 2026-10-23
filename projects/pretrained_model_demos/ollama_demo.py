import json
from urllib.request import Request, ProxyHandler, build_opener

def get_reply(result):
    done = result.get("done")
    reason = result.get("done_reason")

    if done is not True or reason != "stop":
        raise RuntimeError(
            f"Reply not complete: done={done}, reason={reason}, "
            f"generated_tokens={result.get('eval_count')}."
        )

    text = result["message"]["content"]
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Ollama returned no reply text.")

    return text

def main():
    payload = {
        "model": "qwen3:4b",
        "messages": [
            {
                "role": "user",
                "content": "Explain automation in two simple sentences. /no_think",
            }
        ],
        "think": False,
        "stream": False,
        "keep_alive": 0,
        "options": {
            "num_ctx": 2048,
            "num_predict": 256,
        },
    }

    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    opener = build_opener(ProxyHandler({}))
    with opener.open(request, timeout=120) as response:
        result = json.load(response)

    print("Finished:", result.get("done"))
    print("Stop reason:", result.get("done_reason"))
    print("Generated tokens:", result.get("eval_count"))

    text = get_reply(result)

    print("Model:", result["model"])
    print("Returned text:")
    print(text)
    print("Generated tokens:", result.get("eval_count"))
    print("Separate thinking field present:", bool(result["message"].get("thinking")))


if __name__ == "__main__":
    main()