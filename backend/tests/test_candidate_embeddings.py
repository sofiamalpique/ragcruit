import pytest

import app.core.config as config
import app.services.candidate_embeddings as candidate_embeddings
from app.models.candidate import Candidate
from app.services.candidate_embeddings import generate_candidate_embedding


def test_generate_candidate_embedding_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(config, "openai_api_key", None)

    candidate = Candidate(
        full_name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        location="London",
        summary="Pioneer in computing.",
        years_experience=5,
    )

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        generate_candidate_embedding(candidate)


def test_generate_candidate_embedding_calls_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEmbeddingsAPI:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def create(self, *, model: str, input: str, encoding_format: str):
            self.calls.append(
                {
                    "model": model,
                    "input": input,
                    "encoding_format": encoding_format,
                }
            )
            return type(
                "FakeResponse",
                (),
                {"data": [type("FakeEmbedding", (), {"embedding": [0.1, 0.2]})()]},
            )()

    class FakeOpenAI:
        last_instance = None

        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key
            self.embeddings = FakeEmbeddingsAPI()
            FakeOpenAI.last_instance = self

    monkeypatch.setattr(config, "openai_api_key", "test-openai-key")
    monkeypatch.setattr(config, "openai_embedding_model", "text-embedding-3-small")
    monkeypatch.setattr(candidate_embeddings, "OpenAI", FakeOpenAI)

    candidate = Candidate(
        full_name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        location="London",
        summary="Pioneer in computing.",
        years_experience=5,
    )

    embedding = generate_candidate_embedding(candidate)

    assert embedding == [0.1, 0.2]
    assert FakeOpenAI.last_instance is not None
    assert FakeOpenAI.last_instance.api_key == "test-openai-key"
    assert FakeOpenAI.last_instance.embeddings.calls == [
        {
            "model": "text-embedding-3-small",
            "input": (
                "Full name: Ada Lovelace\n"
                "Email: ada@example.com\n"
                "Phone: Not provided\n"
                "Location: London\n"
                "Summary: Pioneer in computing.\n"
                "Years of experience: 5"
            ),
            "encoding_format": "float",
        }
    ]
