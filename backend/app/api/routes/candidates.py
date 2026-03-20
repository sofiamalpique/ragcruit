from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services.candidate_embeddings import generate_candidate_embedding
from app.services.candidate_mapper import candidate_create_to_model


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead, status_code=201)
def create_candidate(
    candidate_in: CandidateCreate,
    db_session: Session = Depends(get_db_session),
) -> CandidateRead:
    candidate = candidate_create_to_model(candidate_in)
    if hasattr(candidate, "embedding"):
        candidate.embedding = generate_candidate_embedding(candidate)
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    return CandidateRead.model_validate(candidate)
