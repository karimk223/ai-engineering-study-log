# AI Engineering Study Log

A collection of small applications built through guided practice in APIs, data storage and applied AI. Each project has its own setup, tests and notes.

## Projects

| Project | Status | What it demonstrates |
| --- | --- | --- |
| [Customer Requests API](projects/fastapi_01_customer_requests/README.md) | Implementation and setup verified | FastAPI, SQLite, validation, CRUD, pagination and isolated tests |
| [ML ticket-routing API](projects/fastapi_02_ml_prediction_api/README.md) | Local implementation verified; 16 cases pass | Text classification, saved-model serving, SQLite logging and result retrieval |
| [LLM/tools API](projects/fastapi_03_llm_tools_api/README.md) | Local implementation verified; 56 cases pass | Hosted LLM, validated native tool calls, checked JSON replies, atomic SQLite logging and failure handling |
| [Computer vision demo](projects/computer_vision_demo/README.md) | Local implementation verified; 8 application tests pass | OpenCV preprocessing, pretrained YuNet detection, DeepFace/ArcFace pairwise verification and isolated tests |

The first project has 51 passing cases in the original, fresh-installation and grouped-project environments. Its own environment passes pip check, and the local server starts successfully from the grouped directory.

## Layout

```text
ai-engineering-study-log/
  README.md
  STUDY-LOG.md
  .gitignore
  projects/
    fastapi_01_customer_requests/
      app/
      tests/
      README.md
      NOTES.md
      requirements.txt
      requirements.lock.txt
    fastapi_02_ml_prediction_api/
      app/
      tests/
      inspect_data.py
      prepare_data_full.py
      split_data_full.py
      train_model_full.py
      README.md
      NOTES.md
      EVALUATION.md
      requirements.txt
      requirements.lock.txt
      data/SOURCE.md
    fastapi_03_llm_tools_api/
      app/
      tests/
      check_llm.py
      .env.example
      README.md
      NOTES.md
      requirements.txt
      requirements.lock.txt
    computer_vision_demo/
      process_image.py
      detect_faces.py
      compare_faces.py
      test_process_image.py
      test_detect_faces.py
      test_compare_faces.py
      README.md
      NOTES.md
      models.sha256
      requirements.txt
      requirements.lock.txt
```

Run setup and test commands from the chosen project's directory. Dependencies and environments are separate for each application.

[Study log](STUDY-LOG.md) records completed work and checks. The larger ingestion/RAG/agents engine and Odoo automation lab are planned as separate repositories.

The [first API milestone](https://github.com/karimk223/ai-engineering-study-log/commit/c48a4db792f6600f752b36d8c557e2bf2da4eeeb) is published. The second project's implementation is recorded in commit `c666b9d`: 99.70% final-test accuracy on its hybrid synthetic corpus, saved-model serving, SQLite logging, GET-by-ID and 16 passing cases. A clean-file rebuild using its existing pinned environment reproduces the model and tests; it was not a separate fresh dependency installation. Unused classifier/review experiments are archived outside this repository's active project.

The third project uses a Groq-hosted model without a local model download. It allows one read-only fictional order lookup and at most two model requests, validates the final reply format, saves completed exchanges and tool traces together, and retrieves saved chats without inference. All 56 cases pass in its own environment and a clean source copy using that same environment. The 25 dependency versions are recorded; a separate fresh dependency installation was not performed. Offline tests use no real credential or provider quota.

The computer-vision exercise uses pretrained models locally on the CPU. Its eight tests cover application behavior using synthetic inputs and controlled detector/comparison replies; they are not a biometric accuracy score. Real photos, generated images, model weights and environments remain ignored. Model download sources/checksums and the distinction between detection, verification and access authorization are documented in the project.

These are local learning applications, not authenticated cloud deployments. The classifier does not reliably reject arbitrary unsupported input, and API 3's controlled-response tests are not a real-model accuracy score. Its saved logs are not conversation memory. The vision demo is not an identification gallery or liveness/access-control system. Further study-log projects remain planned rather than completed skills; see each project's README for exact scope and limitations.
