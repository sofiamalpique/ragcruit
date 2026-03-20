from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.config import database_url
from app.models.base import Base


JOB_POSTING_EMBEDDING_DIMENSIONS = 384
USING_POSTGRESQL = database_url.startswith("postgresql")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_years_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    if USING_POSTGRESQL:
        # Matches the current local embeddings model output size.
        embedding: Mapped[list[float] | None] = mapped_column(
            Vector(JOB_POSTING_EMBEDDING_DIMENSIONS),
            nullable=True,
        )
