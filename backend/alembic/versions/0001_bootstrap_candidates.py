"""Bootstrap candidate table.

Revision ID: 0001
Revises:
Create Date: 2026-03-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

CANDIDATE_EMBEDDING_DIMENSIONS = 384


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _get_column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect_name = bind.dialect.name
    using_postgresql = dialect_name == "postgresql"

    if using_postgresql:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    if not _table_exists(inspector, "candidates"):
        candidate_columns: list[sa.Column] = [
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("location", sa.String(length=255), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("years_experience", sa.Float(), nullable=True),
        ]
        if using_postgresql:
            candidate_columns.append(
                sa.Column(
                    "embedding",
                    Vector(CANDIDATE_EMBEDDING_DIMENSIONS),
                    nullable=True,
                )
            )

        op.create_table(
            "candidates",
            *candidate_columns,
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
    elif using_postgresql and "embedding" not in _get_column_names(
        inspector, "candidates"
    ):
        op.add_column(
            "candidates",
            sa.Column(
                "embedding",
                Vector(CANDIDATE_EMBEDDING_DIMENSIONS),
                nullable=True,
            ),
        )

def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "candidates"):
        op.drop_table("candidates")
