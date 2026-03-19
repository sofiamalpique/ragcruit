from app.models.candidate import Candidate
from app.services.candidate_embedding_text import build_candidate_embedding_text


def generate_candidate_embedding(candidate: Candidate) -> list[float]:
    """Build the future embedding input and fail explicitly until a provider exists."""
    _ = build_candidate_embedding_text(candidate)
    raise NotImplementedError("Candidate embedding generation is not implemented yet.")
