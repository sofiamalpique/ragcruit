from app.models.candidate import Candidate
from app.services.candidate_embedding_text import build_candidate_embedding_text


def test_build_candidate_embedding_text() -> None:
    candidate = Candidate(
        full_name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        location="London",
        summary="Pioneer in computing.",
        years_experience=5,
    )

    assert build_candidate_embedding_text(candidate) == (
        "Full name: Ada Lovelace\n"
        "Email: ada@example.com\n"
        "Phone: Not provided\n"
        "Location: London\n"
        "Summary: Pioneer in computing.\n"
        "Years of experience: 5"
    )
