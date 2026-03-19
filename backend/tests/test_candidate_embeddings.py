import pytest

from app.models.candidate import Candidate
from app.services.candidate_embeddings import generate_candidate_embedding


def test_generate_candidate_embedding_not_implemented() -> None:
    candidate = Candidate(
        full_name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        location="London",
        summary="Pioneer in computing.",
        years_experience=5,
    )

    with pytest.raises(NotImplementedError, match="not implemented"):
        generate_candidate_embedding(candidate)
