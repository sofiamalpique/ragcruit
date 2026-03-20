import app.models.candidate
import app.models.job_posting
from app.db.session import engine
from app.models.base import Base


def create_db_tables() -> None:
    Base.metadata.create_all(bind=engine)
