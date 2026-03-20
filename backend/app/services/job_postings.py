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
