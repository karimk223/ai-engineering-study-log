# AI Engineering Study Log

A collection of small applications built through guided practice in APIs, data storage and applied AI. Each project has its own setup, tests and notes.

## Projects

| Project | Status | What it demonstrates |
| --- | --- | --- |
| [Customer Requests API](projects/fastapi_01_customer_requests/README.md) | Implementation and setup verified | FastAPI, SQLite, validation, CRUD, pagination and isolated tests |
| ML ticket-routing API | Next | Classifying customer messages, model evaluation and API predictions |
| LLM/tools API | Planned | Structured model responses, controlled tool calls and failure handling |

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
```

Run setup and test commands from the chosen project's directory. Dependencies and environments are separate for each application.

[Study log](STUDY-LOG.md) records completed work and checks. The larger ingestion/RAG/agents engine and Odoo automation lab are planned as separate repositories.

Current work is local. GitHub publication is pending. The current API has no AI model, authentication or cloud deployment; later project entries are plans rather than completed skills.
