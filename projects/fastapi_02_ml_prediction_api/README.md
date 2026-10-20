# Customer-support prediction API

A learning project that trains a text classifier, saves it for FastAPI serving, and logs predictions in SQLite. It uses the 11 original customer-support categories, not an LLM.

## Current status

- Data preparation, splitting, training, final evaluation and model persistence are verified.
- Validation: 3,636/3,641 correct (99.86%).
- Final test: 3,631/3,642 correct (99.70%); most-frequent-category baseline: 22.08%.
- Saved model: artifacts/ticket_router_full_v1.joblib, version ticket-router-full-v1.
- FastAPI startup loading, health and POST /predict are verified; local server runs on port 8001.
- SQLite prediction logging and returned row IDs are verified.
- GET /predictions/{prediction_id} retrieves stored results and validates IDs; existing, missing and invalid cases are verified.
- 16 automated API/storage cases pass, including validation, saved-result retrieval and persistence across startup.
- All 28 installed dependency versions match requirements.lock.txt; pip check reports no broken requirements.
- A temporary clean-file rebuild from the pinned raw CSV reproduces the exact data/splits, classifier predictions and 16 passing tests using the existing pinned environment. A separate fresh dependency installation was not performed.
- Local implementation is complete for this learning milestone; commit/push is pending.

These are results on a hybrid synthetic dataset, not representative real-customer accuracy. The classifier always chooses a known category and does not reliably reject arbitrary unsupported inputs. The review-gate experiments are paused and archived separately; they are not part of the active pipeline.

## Active files

- inspect_data.py: verify the raw source checksum and inspect all 11 categories.
- prepare_data_full.py: clean the original raw data directly, check label conflicts and remove normalized duplicates.
- split_data_full.py: create reproducible training/validation/test sets.
- train_model_full.py: train on training data only, report validation/test results, save the pipeline and verify reload predictions.
- app/main.py and app/__init__.py: load the saved model at startup, validate incoming messages and serve predictions/health without retraining.
- app/database.py: initialize the prediction log, store each message/category/score/model version/time in SQLite and retrieve a saved record by ID.
- tests/conftest.py and tests/test_predictions.py: exercise the real saved model/API with a fresh temporary database per test case.
- [Data source](data/SOURCE.md), [evaluation](EVALUATION.md), [notes](NOTES.md).
- requirements.txt and requirements.lock.txt: pinned project dependencies.

The old three-category, OTHER and admission-gate scripts are no longer needed to run this project. Current preparation does not depend on their files.

## Environment

Continue with the existing project environment:

```bash
source .venv/bin/activate
```

For a fresh installation, use Python 3.12, create .venv, then install the pinned requirements:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

## Reproduce the trained model

Place the pinned raw CSV at data/raw/customer_support.csv as documented in [the source record](data/SOURCE.md). From this project directory:

```bash
python inspect_data.py
python prepare_data_full.py
python split_data_full.py
python train_model_full.py
```

The preparation/split commands reproduce the existing cleaned data and split CSVs. The training command evaluates the frozen configuration and writes its model artifact. Do not tune this version using the reported final-test score.

## Run the API

Training happens offline. The API loads the saved model once at startup and reuses it; do not import/run the training script per HTTP request. After generating the model, run from this directory:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Open [Swagger](http://127.0.0.1:8001/docs). Port 8001 is separate from the first project's 8000. POST /predict accepts one message:

```json
{"message": "Please unsubscribe me from your newsletter."}
```

It returns 200, a saved row ID, category SUBSCRIPTION, score about 0.97 and model version ticket-router-full-v1. A score compares the trained categories, not the probability of being correct or in scope. SQLite stores records in predictions.db; startup initializes its table without clearing existing rows.

| Endpoint | Behavior |
| --- | --- |
| GET /health | Status and loaded model version |
| POST /predict | Validate text, predict, save result and return its ID/category/score/version |
| GET /predictions/{prediction_id} | Retrieve the saved message/result/time without classifying again |

Message validation requires a string with 1..2000 characters after trimming and forbids extra fields. Missing/invalid bodies return 422 without saving rows. Prediction IDs must be positive integers no larger than SQLite's signed-64-bit maximum; invalid IDs return 422, absent valid IDs return 404. A missing model file prevents startup with an explanatory error.

## Run the tests

Generate the model first using the reproduction commands above; artifacts are intentionally not committed. Then, with this project's environment active:

```bash
python -m pytest -q
```

Expected: 16 passed. Six test functions produce four individual cases plus seven invalid-body and five invalid-ID cases. They cover startup/health, real prediction, trimmed text, stored-field equality, one-row insertion, missing records, validation/no invalid writes and persistence across two application startups. The isolation fixture redirects DATABASE_PATH to a fresh tmp_path file for each case; lifespan still creates the database normally. Demo predictions.db is not modified.

The pinned Starlette/AnyIO combination emits a known BlockingPortal-alias deprecation warning. It is not a test failure. The temporary clean-file reproduction also passed 16 cases; it reused the existing installed environment and does not establish a separately verified fresh dependency installation.

Only load trusted Joblib files produced by this project's training code, using the compatible pinned environment. Raw data, processed data, artifacts and .venv are excluded from Git. No new model downloads are required.
