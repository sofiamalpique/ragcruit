from pathlib import Path


app_name = "Ragcruit Backend"
version = "0.1.0"

base_dir = Path(__file__).resolve().parents[2]
sqlite_database_path = base_dir / "ragcruit.db"
database_url = f"sqlite:///{sqlite_database_path.as_posix()}"
