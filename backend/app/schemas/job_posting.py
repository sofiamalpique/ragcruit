from pydantic import BaseModel, ConfigDict, Field

from app.schemas.candidate import CandidateRead


class JobPostingBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1)
    company_name: str | None = None
    location: str | None = None
    description: str = Field(min_length=1)
    requirements: str | None = None
    min_years_experience: float | None = Field(default=None, ge=0)


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingRead(JobPostingBase):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    id: int


class JobMatchRequest(BaseModel):
    limit: int = Field(default=5, ge=1)


class JobMatchResult(BaseModel):
    candidate: CandidateRead
    similarity_score: float
    relevance_score: float
    match_reasons: list[str]


class JobMatchResponse(BaseModel):
    results: list[JobMatchResult]
