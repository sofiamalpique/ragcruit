from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateRead,
    CandidateSearchRequest,
    CandidateSearchResponse,
    CandidateSearchResult,
)
from app.services.candidate_embeddings import (
    generate_candidate_embedding,
    generate_text_embedding,
)
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


@router.post("/search", response_model=CandidateSearchResponse)
def search_candidates(
    search_in: CandidateSearchRequest,
    db_session: Session = Depends(get_db_session),
) -> CandidateSearchResponse:
    if not hasattr(Candidate, "embedding"):
        raise HTTPException(
            status_code=503,
            detail=(
                "Candidate semantic search requires PostgreSQL with pgvector-enabled "
                "embeddings."
            ),
        )

    query_embedding = generate_text_embedding(search_in.query_text)
    distance = Candidate.embedding.cosine_distance(query_embedding)
    statement = (
        select(Candidate, distance.label("distance"))
        .where(Candidate.embedding.is_not(None))
        .order_by(distance)
        .limit(search_in.limit)
    )
    rows = db_session.execute(statement).all()
    results = [
        CandidateSearchResult(
            candidate=CandidateRead.model_validate(candidate),
            similarity_score=1.0 / (1.0 + float(distance)),
        )
        for candidate, distance in rows
    ]

    return CandidateSearchResponse(results=results)
