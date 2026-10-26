# Introductory ReAct-style tool agent

A Groq-hosted model connected to a permitted local Python function, with manual and automatic tool-call loops, argument validation and execution limits.

ReAct combines reasoning and acting: choose a next step, take an action through a tool, use its result, and continue or answer. This implementation demonstrates that interaction pattern with native tool calls; it does not reproduce the original paper's prompting experiments or expose internal reasoning. See the [technical notes](NOTES.md) for definitions and code explanations.

## What is implemented

- `tools.py`: integer multiplication with input validation, plus its tool description.
- `manual_agent.py`: one model-requested calculation, an Enter pause, and a second model request for the final answer.
- `automatic_agent.py`: repeated tool/result exchanges without an Enter pause; at most three local tool executions and four model requests.
- An explicit function registry allowing only `multiply`; no `eval` or arbitrary code execution.
- Eight offline test methods: four tool-input checks and four agent-flow checks.

The model is `openai/gpt-oss-120b` hosted by Groq. The arithmetic runs in Python on the application's machine, not inside Groq. Ollama and the sentiment model are not used by these scripts.

## Setup

### Reuse the LLM Tools API environment

These scripts can use the compatible environment from `projects/fastapi_03_llm_tools_api`. From the repository root:

```bash
source projects/fastapi_03_llm_tools_api/.venv/bin/activate
cd projects/llm_agent_demos
python -m unittest discover -v
```

No reinstall is needed for that already-working setup. No API server needs to be running.

### New checkout: optional dedicated environment

From this project's directory, using Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --only-binary=:all: --no-cache-dir -r requirements.txt
python -m pip check
python -m unittest discover -v
```

`requirements.txt` constrains the two direct dependencies with `requirements.lock.txt`. The latter records the 15 installed runtime packages needed by those dependencies, selected from the working API-3 environment's package metadata for Python 3.12.13. It excludes unrelated FastAPI/test-server dependencies, optional extras and pip. It is a version snapshot, not a hash-verified or cross-platform lockfile. The working environment passes pip check. A separate fresh dependency installation has not been performed for this exercise.

### Credentials: live runs only

Both scripts read `projects/fastapi_03_llm_tools_api/.env`, located relative to the script rather than the terminal's current directory. An `.env` in the agent folder is not read.

Preserve the existing private API-3 file. For a new checkout, create it from API 3's blank `.env.example` only if it does not already exist, then enter your own `GROQ_API_KEY` privately in your editor. Do not paste a real key into source, screenshots or Git. A separate OpenAI key is not required. Live requests use Groq and are subject to your account's current model availability and limits.

Tests require neither a real key nor an `.env` file. They use controlled response data and a fake client.

## Run

From this project's directory with the chosen environment active:

```bash
python tools.py
python manual_agent.py
python automatic_agent.py
```

`tools.py` prints `432` without AI. The manual script contacts Groq, displays its tool request, and waits for Enter before calculating and making the follow-up request. The automatic script contacts Groq repeatedly as needed, within its limit. Running either agent script is live inference, not an offline test.

Example output from the automatic agent:

```text
Tool call 1: multiply(18, 24) -> 432
Tool call 2: multiply(432, 3) -> 1296
Final answer: The total cost is 1296 dollars.
```

The question asks for the number of items in 18 boxes of 24, then their cost at 3 dollars each. Actual model wording or the order of multiplication inputs can differ. The final answer is model-generated text, not independently verified by a mathematical answer checker.

## Offline tests

```bash
python -m unittest discover -v
```

Expected: **8 tests, OK**. Local arithmetic traces can appear during the tests; they are not live model calls.

The four tool tests check a normal product, accepted boundary values, wrong input types and out-of-range inputs. Each operand must be an exact Python integer from 0 through 1,000,000; strings, floats, booleans and negative/oversized values are refused.

The four agent tests check actual tool-result content/call ID and final-answer return, a final answer after three permitted calls, refusal before a fourth tool execution, and refusal of an unknown tool without executing the function. `Mock(wraps=multiply)` counts calls while still executing real local arithmetic. Fake response text is predefined test data, not an AI accuracy result.

The saved suite passes in the working environment, including a verification run with real client construction and credential loading blocked. It also passes in a temporary clean source copy using that same interpreter, without an `.env` or copied environment. This is clean-source verification, not a fresh dependency installation.

## Boundaries and limitations

- Only integer multiplication is implemented. No order database, web search, file-writing tool, email action or business-system integration is connected to this agent.
- The automatic loop accepts one tool request at a time and refuses unknown functions and malformed argument shapes before dispatch. The local function checks types/ranges independently of the model's tool schema.
- Three tools may be followed by a fourth model request for the final answer. A request for a fourth tool is refused before execution. Completion/blank checks also apply; this is not an unlimited loop.
- Each model request uses `max_completion_tokens=1024`, low reasoning effort, and no returned reasoning field. The client has a 20-second configured timeout and zero automatic retries. These are not a strict overall wall-clock deadline or a guarantee of server-side cancellation.
- `messages` holds results only during the current run. There is no persistent memory, database logging, user authentication or deployed service.
- Plain-text instructions request a format; they do not guarantee compliance. Terminals print any returned LaTeX notation literally.
- This is a small ReAct-style integration exercise, not a general-purpose or production agent. Selected unit tests and one successful multi-step example do not measure broad reasoning quality, adversarial robustness or every provider/HTTP failure.

## References

- [Original ReAct project and paper](https://react-lm.github.io/)
- [Groq local tool-calling documentation](https://console.groq.com/docs/tool-use/local-tool-calling)
