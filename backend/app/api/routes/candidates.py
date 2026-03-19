from fastapi import APIRouter

from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services.candidate_mapper import candidate_create_to_model


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead, status_code=201)
def create_candidate(candidate_in: CandidateCreate) -> CandidateRead:
    candidate = candidate_create_to_model(candidate_in)

    return CandidateRead(
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        summary=candidate.summary,
        years_experience=candidate.years_experience,
        skills=candidate_in.skills,
    )
