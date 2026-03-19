import os
from pathlib import Path


app_name = "Ragcruit Backend"
version = "0.1.0"

base_dir = Path(__file__).resolve().parents[2]
default_sqlite_database_path = base_dir / "ragcruit.db"
default_database_url = f"sqlite:///{default_sqlite_database_path.as_posix()}"
database_url = os.getenv("DATABASE_URL", default_database_url)
