"""Add job_postings table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-20 00:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

JOB_POSTING_EMBEDDING_DIMENSIONS = 384


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _get_column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    using_postgresql = bind.dialect.name == "postgresql"

    if not _table_exists(inspector, "job_postings"):
        job_posting_columns: list[sa.Column] = [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("company_name", sa.String(length=255), nullable=True),
            sa.Column("location", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("requirements", sa.Text(), nullable=True),
            sa.Column("min_years_experience", sa.Float(), nullable=True),
        ]
        if using_postgresql:
            job_posting_columns.append(
                sa.Column(
                    "embedding",
                    Vector(JOB_POSTING_EMBEDDING_DIMENSIONS),
                    nullable=True,
                )
            )

        op.create_table(
            "job_postings",
            *job_posting_columns,
            sa.PrimaryKeyConstraint("id"),
        )
    elif using_postgresql and "embedding" not in _get_column_names(
        inspector, "job_postings"
    ):
        op.add_column(
            "job_postings",
            sa.Column(
                "embedding",
                Vector(JOB_POSTING_EMBEDDING_DIMENSIONS),
                nullable=True,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "job_postings"):
        op.drop_table("job_postings")
