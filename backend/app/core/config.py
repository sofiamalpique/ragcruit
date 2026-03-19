import os
from pathlib import Path


app_name = "Ragcruit Backend"
version = "0.1.0"

base_dir = Path(__file__).resolve().parents[2]
default_sqlite_database_path = base_dir / "ragcruit.db"
default_database_url = f"sqlite:///{default_sqlite_database_path.as_posix()}"
database_url = os.getenv("DATABASE_URL", default_database_url)
using_default_database_url = "DATABASE_URL" not in os.environ
using_local_sqlite_fallback = using_default_database_url and database_url == default_database_url
should_create_tables_on_startup = using_local_sqlite_fallback
