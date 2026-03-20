import app.core.config as config
import app.services.candidate_embeddings as candidate_embeddings
from app.models.candidate import Candidate
from app.services.candidate_embeddings import (
    generate_candidate_embedding,
    generate_text_embedding,
)


def test_get_embedding_model_uses_configured_model_name(
    monkeypatch,
) -> None:
    class FakeSentenceTransformer:
        last_model_name = None

        def __init__(self, model_name: str) -> None:
            FakeSentenceTransformer.last_model_name = model_name

    monkeypatch.setattr(
        config,
        "embedding_model_name",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    monkeypatch.setattr(
        candidate_embeddings,
        "SentenceTransformer",
        FakeSentenceTransformer,
    )
    monkeypatch.setattr(candidate_embeddings, "_embedding_model", None)

    candidate_embeddings.get_embedding_model()

    assert (
        FakeSentenceTransformer.last_model_name
        == "sentence-transformers/all-MiniLM-L6-v2"
    )


def test_generate_candidate_embedding_uses_local_model(monkeypatch) -> None:
    class FakeEmbedding:
        def __init__(self, values: list[float]) -> None:
            self.values = values

        def tolist(self) -> list[float]:
            return self.values

    class FakeSentenceTransformer:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def encode(self, text: str) -> FakeEmbedding:
            self.calls.append(text)
            return FakeEmbedding([0.1, 0.2, 0.3])

    fake_model = FakeSentenceTransformer()
    monkeypatch.setattr(candidate_embeddings, "get_embedding_model", lambda: fake_model)

    candidate = Candidate(
        full_name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        location="London",
        summary="Pioneer in computing.",
        years_experience=5,
    )

    embedding = generate_candidate_embedding(candidate)

    assert embedding == [0.1, 0.2, 0.3]
    assert fake_model.calls == [
        (
            "Full name: Ada Lovelace\n"
            "Email: ada@example.com\n"
            "Phone: Not provided\n"
            "Location: London\n"
            "Summary: Pioneer in computing.\n"
            "Years of experience: 5"
        )
    ]


def test_generate_text_embedding_uses_local_model(monkeypatch) -> None:
    class FakeEmbedding:
        def __init__(self, values: list[float]) -> None:
            self.values = values

        def tolist(self) -> list[float]:
            return self.values

    class FakeSentenceTransformer:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def encode(self, text: str) -> FakeEmbedding:
            self.calls.append(text)
            return FakeEmbedding([0.4, 0.5, 0.6])

    fake_model = FakeSentenceTransformer()
    monkeypatch.setattr(candidate_embeddings, "get_embedding_model", lambda: fake_model)

    embedding = generate_text_embedding("Find a machine learning engineer")

    assert embedding == [0.4, 0.5, 0.6]
    assert fake_model.calls == ["Find a machine learning engineer"]
