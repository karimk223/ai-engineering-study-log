# ML prediction API — compact notes

## Data and evaluation

- A classification model predicts one of the labels it learned. This project keeps all 11 original customer-support categories.
- instruction is the input message; category is the known answer. Source responses and labels are not input features.
- Clean missing/blank rows and whitespace, check conflicting labels, and remove case-insensitive duplicate messages before splitting.
- Current data: 24,274 unique messages; train 16,991, validation 3,641, final test 3,642.
- Stratification keeps similar category proportions. random_state=42 reproduces the shuffle for the same data/setup.
- Training learns parameters; validation supports development choices; final testing measures the frozen version. Never fit or retune on test labels.
- Exact duplicate separation does not prevent similar generated templates from appearing in multiple sets.

## Model

- TF-IDF turns words and two-word phrases into weighted numeric features, learning vocabulary/weights from training only.
- Logistic regression learns category weights from those features. It is a classifier, not an LLM.
- Pipeline combines text conversion and classification. fit learns; predict reuses the learned pipeline.
- The baseline always answers ACCOUNT, the most common training category. It achieves about 22.08% accuracy.
- Current model: 99.86% validation accuracy; 99.70% final-test accuracy (3,631/3,642 correct).
- Precision concerns answers predicted as a category; recall concerns actual examples of that category. F1 combines them; support is the number of examples. Macro F1 weights categories equally.
- These scores describe the hybrid synthetic dataset, not every possible customer message.

## Saving and serving

- Joblib saves the whole pipeline, including text conversion, plus model/library version and categories.
- Current artifact: artifacts/ticket_router_full_v1.joblib, model version ticket-router-full-v1.
- Loading the saved model preserves predictions. Load only our own trusted artifact with compatible dependencies.
- Training runs offline. FastAPI will load the saved file once at startup, then reuse it for requests; no retraining per request.
- A model score compares its trained categories; it does not prove the answer is correct or that an input is supported.
- Unknown-input rejection research is paused. The current baseline is for supported customer-service messages; no reliable MANUAL_REVIEW feature is claimed.
- Health and prediction endpoints are now verified locally. Startup restores the bundle with joblib.load; POST retrieves bundle["pipeline"] and uses predict_proba. The shared saved file connects the training and API scripts; using the same variable name does not connect them.
- SQLite logging is now verified: POST stores message/category/score/model version/time and returns the inserted row ID. init_database runs at startup with CREATE TABLE IF NOT EXISTS; save_prediction uses SQL parameters and commit, and closes its connection.
- GET by ID is verified: return stored fields with 200; absent valid ID gives 404; invalid/nonpositive/overflow ID gives 422. GET reads stored results and does not rerun classification. Logging does not retrain the model.
- Six test functions now run 16 cases: four individual, seven invalid bodies, five invalid IDs. The autouse fixture redirects DATABASE_PATH to a temporary file per case; normal app startup still creates the table. Tests use the real saved model and verify API/storage behavior, not a new accuracy estimate.
- All 16 pass, including saved-record equality after application restart. Demo history/model stay unchanged. A known Starlette/AnyIO dependency deprecation warning is not a failing test.
- A temporary clean-file rebuild from raw data reproduces the data, splits, trained predictions and all 16 cases using the existing pinned environment. This is not an independent fresh dependency-install test. All 28 pinned installed versions match; pip check passes.
- Next: commit/push this completed local API milestone to the existing study-log repository. No new model/gate work or dependency installation is required.
