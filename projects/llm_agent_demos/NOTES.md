# Learning notes: introductory ReAct agent

## What is an agent?

Here, an agent is a program that uses a language model to choose a next action and permitted tools to carry it out. The model alone does not execute our Python functions. Our application checks the request, runs the allowed function, and gives the result back.

## What does ReAct mean?

ReAct combines **reasoning and acting**. In simple terms: decide a useful next step, take an action, read what happened, then decide again. The returned result is often called an **observation**. The [original research](https://react-lm.github.io/) interleaves reasoning with actions and observations. Our introductory native-tool loop demonstrates the interaction pattern, not the paper's full prompting setup or benchmark results. It does not print or establish a faithful account of internal model reasoning.

It is not the React website interface library, a new model we trained, or another model download.

## Our example

The question supplies 18 boxes, 24 items per box, and a price of 3 dollars per item.

1. The model requests `multiply(18, 24)`.
2. Python returns `432`: the item count.
3. The model requests `multiply(432, 3)`, using the first result.
4. Python returns `1296`: the total cost.
5. The model writes its final answer.

Karim's October 26 run showed those two real local tool executions followed by the 1296-dollar answer. Arithmetic is deliberately simple so the model/tool handoff is visible. The same interaction idea appears in API 3's fictional order-status lookup, but this agent is not connected to that order tool.

## What is a tool?

A tool is ordinary code with a limited job. `multiply` accepts two integers, validates them and returns their product. Its **schema**, `MULTIPLY_TOOL`, is a description sent to the model: name, purpose, input names/types and bounds. Sending the description does not send control of the laptop to the model or execute the function.

The model returns a structured request with a name, JSON arguments and an ID. `json.loads` converts the argument text into a Python dictionary; it does not execute Python. The application allows only the exact `a`/`b` keys and checks the permitted name. The function itself rejects unsuitable types/ranges. A schema is not a substitute for these local checks.

## Where does the AI run, and where does Python run?

`client.chat.completions.create(...)` sends the conversation and tool description to the model hosted by Groq. `TOOL_FUNCTIONS[name](**arguments)` executes our selected local function. With `{"a": 18, "b": 24}`, the latter means `multiply(a=18, b=24)`.

The explicit registry `{"multiply": multiply}` connects one allowed name to its actual function. We do not use `eval` or execute arbitrary code from a model response. Groq is the provider; `openai/gpt-oss-120b` is the model identifier; the surrounding loop and safeguards are our application. See [Groq's tool-calling explanation](https://console.groq.com/docs/tool-use/local-tool-calling).

## How does the result reach the AI?

The program adds the assistant's request to `messages`, then adds a `role="tool"` message containing the actual result. `tool_call_id` matches the original request ID, like attaching an answer to the right question. The next model request includes those messages. Without sending the result, merely calculating or printing `432` does not tell the model what happened.

This message list is temporary context, not training or permanent memory. Each call to `run_agent` starts a new list.

## Manual versus automatic

The manual version has one tool execution after an Enter pause, then a fixed second request using `tool_choice="none"` to request the final answer.

The automatic version repeatedly uses `tool_choice="auto"`. It either receives a final reply and returns it, or validates/runs a requested tool, adds its result, and repeats. Removing the Enter pause alone would not create this repeated control flow.

`MAX_TOOL_CALLS=3` limits local actions. At most four model requests are allowed: three may request permitted calculations, and one more can produce the final answer. If that last request asks for another tool, Python refuses before execution. This action budget is different from `max_completion_tokens=1024`, which caps newly generated tokens within each model request. Token limits do not count words or permitted tool executions.

## What did the tests check?

Four tool tests check calculation, boundary values, unsuitable types and out-of-range inputs. Four agent tests use a fake client with replies we choose. They check result/call-ID handling, an answer after three tools, refusal before a fourth tool, and refusal of an unknown tool.

`Mock()` is a stand-in, not another AI. `Mock(wraps=multiply)` still runs our actual arithmetic while counting executions. A test deliberately supplying a forbidden request passes when the expected refusal occurs. These tests check our Python rules; they do not measure real-model intelligence or accuracy. Live runs, offline tests, clean-source tests and fresh dependency installations are different evidence levels.

## Why did the manual answer show backslashes?

The model used LaTeX math formatting: `\(...\)` surrounds a formula and `\times` represents multiplication. The terminal prints these characters rather than typesetting them. The arithmetic was correct. A plain-text instruction requests a simpler style but cannot guarantee every future reply's format.

## Interview explanation

"I built a small tool-using agent with a hosted model and local Python arithmetic. The model requests a named tool; Python checks its name and arguments, runs it and returns the result with the matching call ID. A bounded loop allows further actions or a final answer, with a maximum of three tool executions. I tested the tool rules and loop behavior with controlled replies, separately from the live demonstration."

This demonstrates introductory integration, not autonomous permission for arbitrary actions, production readiness or a broad model evaluation.
