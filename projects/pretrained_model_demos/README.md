# Pretrained model demos

## Implemented: local sentiment classification

A small Python script loads an existing English sentiment model, checks six example sentences and prints POSITIVE or NEGATIVE with a model score. The model was trained by others; this project integrates it for local inference, not training or chatbot generation.

The current lesson uses [DistilBERT fine-tuned on SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) at revision `714eb0fa89d2f80546fda750413ed43d93601a13`. Transformers loads the tokenizer/model and PyTorch runs the calculations on the CPU. No hosted inference service, API key or paid model call is used.

Only this sentiment exercise is implemented here. Ollama and other roadmap exercises remain planned.

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

## One-time model download

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

## Run locally, offline

```bash
python sentiment_demo.py
```

The script sets project-local cache paths and offline mode before importing Transformers. Both loaders use `local_files_only=True` and `trust_remote_code=False`; model loading requests Safetensors. Missing files must be supplied before running inference; the script does not download them automatically.

The six hard-coded sentences are processed together in one model call. Each must be nonblank and have at most 512 token IDs, including special markers. An invalid sentence raises `ValueError` and stops the whole batch before prediction. Weights currently load before those checks, so a loading progress bar can appear before an input error.

Observed learner-run results, rounded to four decimals:

| Text | Prediction | Model score |
| --- | --- | --- |
| I enjoyed this movie. | POSITIVE | 0.9999 |
| I did not enjoy this movie. | NEGATIVE | 0.9986 |
| This movie was bad. | NEGATIVE | 0.9998 |
| This movie was not bad. | POSITIVE | 0.9991 |
| The movie lasts two hours. | NEGATIVE | 0.9750 |
| Great, another three-hour delay. | POSITIVE | 0.6002 |

These are qualitative probes, not a measured accuracy score. The factual fifth sentence has no clear sentiment, but this model has no neutral label. The sixth result misses the likely sarcastic complaint. A high model score does not guarantee correctness.

## Tests

```bash
python -m unittest -v test_sentiment_demo.py
```

Four methods pass: short text accepted, blank/whitespace text rejected, exactly 512 tokens accepted and 513 rejected. A controlled pretend tokenizer (`Mock`) returns the requested token count. These tests need the installed libraries but not model files, network access or real predictions. They check Python's input rules, not real token splitting or model accuracy. The blank-text method includes two subcases, still counted as one method.

The four tests also pass in a temporary clean source copy with no `storage` or `.venv`, using the existing project's interpreter. Both pretrained-loader methods were blocked during this check and were never called. This verifies test isolation, not a fresh dependency installation. The temporary copy was removed automatically.

Manual checks also rejected a whitespace-only seventh sentence and a seventh sentence consisting of `This movie was good. ` repeated 150 times (752 tokens). That extra item was removed afterward. A prior tokenizer-only lesson showed 752 tokens shortened to 512; the long input was not forwarded through the model.

## Limitations and runtime evidence

- This is a fixed-example batch script, not a deployed API, interactive chatbot, long-document workflow or feedback-training system.
- Only English positive/negative classification is provided. Neutrality, sarcasm and unfamiliar domains need evaluation; the code has no abstention or neutral class.
- Input checks apply to individual strings in this demo's batch; they are not a complete public API schema or an empty-batch/type validator.
- A single-sentence CPU forward crashed with a native bus error in the installed-runtime preflight, at the model's pre-classification linear layer. Two- and six-sentence batches ran successfully. The cause is unresolved; batching is the demonstrated path, not a proven fix. Single-input deployment is not validated.
- The passing unit tests do not exercise that native model-forward path. `pip check` checks declared dependency compatibility, not runtime correctness.

Model files, caches and `.venv` remain ignored under the repository's existing rules. Only source, tests, dependency records, notes and checksums belong in Git. See [learning notes](NOTES.md) for a plain-language explanation of the code.
