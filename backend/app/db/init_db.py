import app.models.candidate
from app.db.session import engine
from app.models.base import Base


def create_db_tables() -> None:
    Base.metadata.create_all(bind=engine)
