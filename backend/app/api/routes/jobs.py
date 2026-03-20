from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.schemas.candidate import CandidateRead
from app.schemas.job_posting import (
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    JobPostingCreate,
    JobPostingRead,
)
from app.services.candidate_embeddings import generate_text_embedding
from app.services.job_postings import (
    build_job_match_insights,
    build_job_posting_embedding_text,
    job_posting_create_to_model,
)


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobPostingRead, status_code=201)
def create_job_posting(
    job_in: JobPostingCreate,
    db_session: Session = Depends(get_db_session),
) -> JobPostingRead:
    job_posting = job_posting_create_to_model(job_in)
    if hasattr(job_posting, "embedding"):
        job_posting.embedding = generate_text_embedding(
            build_job_posting_embedding_text(job_posting)
        )
    db_session.add(job_posting)
    db_session.commit()
    db_session.refresh(job_posting)

    return JobPostingRead.model_validate(job_posting)


@router.get("", response_model=list[JobPostingRead])
def list_job_postings(
    db_session: Session = Depends(get_db_session),
) -> list[JobPostingRead]:
    statement = select(JobPosting).order_by(JobPosting.id.desc())
    job_postings = db_session.scalars(statement).all()
    return [JobPostingRead.model_validate(job_posting) for job_posting in job_postings]


@router.get("/{job_posting_id}", response_model=JobPostingRead)
def get_job_posting(
    job_posting_id: int,
    db_session: Session = Depends(get_db_session),
) -> JobPostingRead:
    job_posting = db_session.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    return JobPostingRead.model_validate(job_posting)


@router.post("/{job_posting_id}/match", response_model=JobMatchResponse)
def match_candidates_to_job_posting(
    job_posting_id: int,
    match_in: JobMatchRequest,
    db_session: Session = Depends(get_db_session),
) -> JobMatchResponse:
    if not hasattr(JobPosting, "embedding") or not hasattr(Candidate, "embedding"):
        raise HTTPException(
            status_code=503,
            detail=(
                "Job matching requires PostgreSQL with pgvector-enabled embeddings."
            ),
        )

    job_posting = db_session.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found.")
    if job_posting.embedding is None:
        raise HTTPException(
            status_code=409,
            detail="Job posting does not have a persisted embedding.",
        )

    distance = Candidate.embedding.cosine_distance(job_posting.embedding)
    statement = (
        select(Candidate, distance.label("distance"))
        .where(Candidate.embedding.is_not(None))
        .order_by(distance)
        .limit(match_in.limit)
    )
    rows = db_session.execute(statement).all()
    results: list[JobMatchResult] = []
    for candidate, distance in rows:
        similarity_score = 1.0 / (1.0 + float(distance))
        relevance_score, match_reasons = build_job_match_insights(
            job_posting=job_posting,
            candidate=candidate,
            similarity_score=similarity_score,
        )
        results.append(
            JobMatchResult(
                candidate=CandidateRead.model_validate(candidate),
                similarity_score=similarity_score,
                relevance_score=relevance_score,
                match_reasons=match_reasons,
            )
        )

    return JobMatchResponse(results=results)
