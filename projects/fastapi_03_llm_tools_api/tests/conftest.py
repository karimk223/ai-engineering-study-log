from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import database, main


@pytest.fixture
def api(tmp_path, monkeypatch):
    fake_llm = MagicMock()
    fake_llm.__enter__.return_value = fake_llm
    fake_llm.chat.completions.create.side_effect = AssertionError(
        "Unexpected AI call in this test"
    )

    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test_chats.db"
    )
    monkeypatch.setattr(
        main,
        "dotenv_values",
        lambda *args, **kwargs: {"GROQ_API_KEY": "test-only-not-real"},
    )
    monkeypatch.setattr(
        main.groq, "Groq", lambda **kwargs: fake_llm
    )

    with TestClient(main.app) as client:
        yield client, fake_llm