from sentence_transformers import SentenceTransformer

import app.core.config as config
from app.models.candidate import Candidate
from app.services.candidate_embedding_text import build_candidate_embedding_text

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(config.embedding_model_name)

    return _embedding_model


def generate_candidate_embedding(candidate: Candidate) -> list[float]:
    candidate_text = build_candidate_embedding_text(candidate)
    embedding = get_embedding_model().encode(candidate_text)
    return embedding.tolist()
