from pydantic import BaseModel, ConfigDict, Field


class CandidateBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    years_experience: float | None = Field(default=None, ge=0)


class CandidateCreate(CandidateBase):
    skills: list[str] = Field(default_factory=list)


class CandidateRead(CandidateBase):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    id: int
