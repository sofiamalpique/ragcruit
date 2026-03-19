from app.models.candidate import Candidate


def build_candidate_embedding_text(candidate: Candidate) -> str:
    years_experience = (
        f"{candidate.years_experience:g}"
        if candidate.years_experience is not None
        else "Not provided"
    )

    lines = [
        f"Full name: {candidate.full_name}",
        f"Email: {candidate.email}",
        f"Phone: {candidate.phone or 'Not provided'}",
        f"Location: {candidate.location or 'Not provided'}",
        f"Summary: {candidate.summary or 'Not provided'}",
        f"Years of experience: {years_experience}",
    ]

    return "\n".join(lines)
