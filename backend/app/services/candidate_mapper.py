from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


def candidate_create_to_model(candidate_in: CandidateCreate) -> Candidate:
    return Candidate(**candidate_in.model_dump(exclude={"skills"}))
