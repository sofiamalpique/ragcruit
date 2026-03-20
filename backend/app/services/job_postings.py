from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate


def job_posting_create_to_model(job_in: JobPostingCreate) -> JobPosting:
    return JobPosting(**job_in.model_dump())


def build_job_posting_embedding_text(job: JobPosting) -> str:
    company_name = job.company_name if job.company_name else "Not provided"
    location = job.location if job.location else "Not provided"
    requirements = job.requirements if job.requirements else "Not provided"
    min_years_experience = (
        str(job.min_years_experience)
        if job.min_years_experience is not None
        else "Not provided"
    )

    return (
        f"Title: {job.title}\n"
        f"Company: {company_name}\n"
        f"Location: {location}\n"
        f"Description: {job.description}\n"
        f"Requirements: {requirements}\n"
        f"Minimum years of experience: {min_years_experience}"
    )


def _normalize_location(location: str | None) -> str | None:
    if location is None:
        return None

    normalized_location = location.strip().casefold()
    return normalized_location or None


def build_job_match_insights(
    job_posting: JobPosting,
    candidate: Candidate,
    similarity_score: float,
) -> tuple[float, list[str]]:
    relevance_score = similarity_score
    match_reasons: list[str] = []

    if similarity_score >= 0.75:
        match_reasons.append("Strong semantic match to the job description")
    else:
        match_reasons.append("Semantic match to the job description")

    if (
        job_posting.min_years_experience is not None
        and candidate.years_experience is not None
        and candidate.years_experience >= job_posting.min_years_experience
    ):
        relevance_score += 0.1
        match_reasons.append("Experience meets the minimum requirement")

    candidate_location = _normalize_location(candidate.location)
    job_location = _normalize_location(job_posting.location)
    if (
        candidate_location is not None
        and job_location is not None
        and candidate_location == job_location
    ):
        relevance_score += 0.05
        match_reasons.append("Location matches the job posting")

    relevance_score = max(0.0, min(relevance_score, 1.0))
    return relevance_score, match_reasons
