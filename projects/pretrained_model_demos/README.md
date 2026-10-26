# Pretrained model demos

Local sentiment classification with Transformers/PyTorch and text generation through Ollama's local API. Both use pretrained models.

## Implemented: local sentiment classification

A small Python script loads an existing English sentiment model, checks six example sentences and prints POSITIVE or NEGATIVE with a model score. The model was trained by others; this project integrates it for local inference, not training or chatbot generation.

The script uses [DistilBERT fine-tuned on SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) at revision `714eb0fa89d2f80546fda750413ed43d93601a13`. Transformers loads the tokenizer/model and PyTorch runs the calculations on the CPU. No hosted inference service, API key or paid model call is used.

The Ollama client is documented below. Tool-using agents are implemented in the separate [ReAct-style agent project](../llm_agent_demos/README.md).

## Environment and dependencies

Verified in the existing macOS Apple Silicon environment with Python 3.12.13, PyTorch 2.14.1 and Transformers 5.20.2. `pip check` passes. The 34 entries in `requirements.lock.txt` record installed versions; this is not a package-hash lock or a cross-platform compatibility guarantee. A separate fresh dependency installation has not been tested.

Run commands from this project's directory. For an initial setup:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --only-binary=:all: -r requirements.txt
python -m pip check
```

For the already-working environment, activate it without reinstalling:

```bash
source .venv/bin/activate
```

## Sentiment model download

This step needs network access and roughly 268 MB for the weights, plus the small configuration/vocabulary files and temporary download space. It is separate from installing Python libraries. Do not run it again if the four files are already present and pass the checksum check.

The command selects only the four required files from the pinned revision, avoiding duplicate weight formats. It does not send example sentences to a service.

```bash
export HF_HOME="$PWD/storage/huggingface"
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1

HF_HUB_OFFLINE=0 hf download \
  distilbert/distilbert-base-uncased-finetuned-sst-2-english \
  config.json tokenizer_config.json vocab.txt model.safetensors \
  --revision 714eb0fa89d2f80546fda750413ed43d93601a13 \
  --local-dir storage/models/sentiment

shasum -a 256 -c models.sha256
```

The manifest covers all four files. Checksums identify the expected bytes; they do not establish prediction quality or runtime compatibility. See the [pinned revision](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english/commit/714eb0fa89d2f80546fda750413ed43d93601a13) and [Hub download documentation](https://huggingface.co/docs/huggingface_hub/guides/download).

## Run sentiment locally, offline

```bash
python sentiment_demo.py
```

The script sets project-local cache paths and offline mode before importing Transformers. Both loaders use `local_files_only=True` and `trust_remote_code=False`; model loading requests Safetensors. Missing files must be supplied before running inference; the script does not download them automatically.

The six hard-coded sentences are processed together in one model call. Each must be nonblank and have at most 512 token IDs, including special markers. An invalid sentence raises `ValueError` and stops the whole batch before prediction. Weights currently load before those checks, so a loading progress bar can appear before an input error.

Example inference results, rounded to four decimals:

| Text | Prediction | Model score |
| --- | --- | --- |
| I enjoyed this movie. | POSITIVE | 0.9999 |
| I did not enjoy this movie. | NEGATIVE | 0.9986 |
| This movie was bad. | NEGATIVE | 0.9998 |
| This movie was not bad. | POSITIVE | 0.9991 |
| The movie lasts two hours. | NEGATIVE | 0.9750 |
| Great, another three-hour delay. | POSITIVE | 0.6002 |

These are qualitative probes, not a measured accuracy score. The factual fifth sentence has no clear sentiment, but this model has no neutral label. The sixth result misses the likely sarcastic complaint. A high model score does not guarantee correctness.

## Sentiment input tests

```bash
python -m unittest -v test_sentiment_demo.py
```

Four methods pass: short text accepted, blank/whitespace text rejected, exactly 512 tokens accepted and 513 rejected. A controlled pretend tokenizer (`Mock`) returns the requested token count. These tests need the installed libraries but not model files, network access or real predictions. They check Python's input rules, not real token splitting or model accuracy. The blank-text method includes two subcases, still counted as one method.

The four tests also pass in a temporary clean source copy with no `storage` or `.venv`, using the existing project's interpreter. Both pretrained-loader methods were blocked during this check and were never called. This verifies test isolation, not a fresh dependency installation. The temporary copy was removed automatically.

## Sentiment limitations and runtime evidence

- This is a fixed-example batch script, not a deployed API, interactive chatbot, long-document workflow or feedback-training system.
- Only English positive/negative classification is provided. Neutrality, sarcasm and unfamiliar domains need evaluation; the code has no abstention or neutral class.
- Input checks apply to individual strings in this demo's batch; they are not a complete public API schema or an empty-batch/type validator.
- A single-sentence CPU forward crashed with a native bus error in the installed-runtime preflight, at the model's pre-classification linear layer. Two- and six-sentence batches ran successfully. The cause is unresolved; batching is the demonstrated path, not a proven fix. Single-input deployment is not validated.
- The passing unit tests do not exercise that native model-forward path. `pip check` checks declared dependency compatibility, not runtime correctness.

Model files, caches and `.venv` remain ignored under the repository's rules. See [technical notes](NOTES.md) for an explanation of the implementation.

## Implemented: local text generation with Ollama

`ollama_demo.py` sends one fixed English question to Qwen3:4b through `http://127.0.0.1:11434/api/chat`. Ollama runs the model on this computer; Python sends a JSON POST and reads its JSON response. It is a client of Ollama, not a new FastAPI server or a hosted-provider call.

Tested with Ollama 0.40.9 and Python 3.12.13 on macOS. The script uses Python's standard-library `json` and `urllib.request`; it does not require the Ollama Python SDK.

### Setup and one-time download

Install the macOS app using [Ollama's official manual download](https://ollama.com/download/mac) and [installation instructions](https://docs.ollama.com/macos). Open it, choose local use without signing in, and enable its terminal command if prompted. Keep the local service running when calling it from Python.

Check the installation and existing models:

```bash
ollama --version
ollama list
```

Only if the model is not already downloaded:

```bash
ollama pull qwen3:4b
```

The selected model is roughly 2.5 GB, separate from Python packages. Downloading needs internet access; subsequent inference with this cached local model does not need a hosted inference service or account. Ollama normally stores its cache outside this repository in the user's `.ollama/models` directory. Do not copy that directory or its weights into Git.

[OLLAMA-MODEL.md](OLLAMA-MODEL.md) records the observed model digests and quantization. The tag `qwen3:4b` can change upstream; this script uses that tag, not an immutable model pin. Recording digests does not make a later fresh pull identical or establish prediction quality.

### Run the Python client

From this project directory, using the existing environment:

```bash
source .venv/bin/activate
python ollama_demo.py
```

The request specifies `think=false`, `stream=false`, `keep_alive=0`, a 2,048-token context window and at most 256 newly generated tokens. The prompt also includes `/no_think`. The proxy-free opener targets the fixed loopback address. A 120-second I/O timeout is not a hard total-duration deadline or guaranteed server-side cancellation. After the request, `keep_alive=0` requests unloading from memory, not deletion of downloaded files.

`get_reply` requires `done=true`, `done_reason=stop` and nonblank string content. Other finish reasons raise an error that includes the actual metadata; reaching the generation limit can leave an incomplete reply. Transport, JSON and unexpected response-shape errors are not comprehensively translated into friendly messages by this small client.

An example response reported `done=true`, `done_reason=stop` and 246 generated tokens. Content still included planning-like text and a closing think tag before the final answer; the separate thinking field was absent. The program prints this content unchanged. Normal completion does not establish correctness, brevity or successful thinking suppression.

### Reply tests and all-project tests

```bash
python -m unittest -v test_ollama_demo.py
python -m unittest discover -v
```

The Ollama file has four passing methods: accept completed text; reject an unfinished result; reject a simulated length-limited result; reject empty, whitespace-only or non-string content. The last method has three subcases. These tests call the helper with controlled dictionaries; they do not contact Ollama, run Qwen, load weights or prove the actual model's cutoff behavior.

Combined discovery passes all eight methods across both demos. A clean-source check using the existing interpreter also passes without copied model files or an Ollama service call. This is test isolation, not a new dependency installation or an end-to-end inference test.

### Observed limitations

- `--think=false` alone still produced lengthy planning-like text. Adding `/no_think` shortened one observed reply but did not reliably suppress that text. No template-repair or model-replacement claim is made.
- The four reply tests cover the helper's completion/content rules, not HTTP errors, every malformed JSON shape, model accuracy or all request settings.
- The script sends one user message per request. It has no implemented conversation memory, tool execution, retrieval, application authentication or deployment.
- Unlike API 3's hosted Groq service, this exercise uses local compute and storage. The different models and tasks were not evaluated in a fair quality/speed comparison. Neither deployment location guarantees truthful answers.

See the [chat API](https://docs.ollama.com/api/chat), [thinking controls](https://docs.ollama.com/capabilities/thinking) and [Qwen's soft prompt switch](https://qwenlm.github.io/blog/qwen3/#advanced-usages). Prompt instructions and accepted settings must be checked against actual outputs, not assumed to work perfectly.
