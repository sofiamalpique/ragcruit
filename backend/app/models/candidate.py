from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.config import database_url
from app.models.base import Base


CANDIDATE_EMBEDDING_DIMENSIONS = 384
USING_POSTGRESQL = database_url.startswith("postgresql")


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    if USING_POSTGRESQL:
        # Matches the current local embeddings model output size.
        embedding: Mapped[list[float] | None] = mapped_column(
            Vector(CANDIDATE_EMBEDDING_DIMENSIONS),
            nullable=True,
        )

    # Skills are intentionally omitted until we choose a clearer storage shape
    # such as a normalized relation or a structured document field.
