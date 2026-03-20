from fastapi.testclient import TestClient
from sqlalchemy import delete, select

import app.api.routes.candidates as candidate_routes
from app.db.session import get_db_session
from app.db.session import SessionLocal
from app.models.candidate import Candidate
from app.main import app


def test_create_candidate_endpoint() -> None:
    with TestClient(app) as client:
        with SessionLocal() as session:
            session.execute(delete(Candidate))
            session.commit()

        response = client.post(
            "/candidates",
            json={
                "full_name": "Ada Lovelace",
                "email": "ada@example.com",
                "phone": "+351123456789",
                "location": "Lisbon",
                "summary": "Pioneer in computing.",
                "years_experience": 5,
                "skills": ["python", "machine learning"],
            },
        )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data == {
        "id": response_data["id"],
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "phone": "+351123456789",
        "location": "Lisbon",
        "summary": "Pioneer in computing.",
        "years_experience": 5.0,
    }
    assert isinstance(response_data["id"], int)
    assert "skills" not in response_data

    with SessionLocal() as session:
        stored_candidate = session.scalar(
            select(Candidate).where(Candidate.id == response_data["id"])
        )

    assert stored_candidate is not None
    assert stored_candidate.full_name == "Ada Lovelace"
    assert stored_candidate.email == "ada@example.com"


def test_search_candidates_endpoint(monkeypatch) -> None:
    class FakeDistance:
        def label(self, _: str) -> "FakeDistance":
            return self

    class FakeEmbeddingColumn:
        def __init__(self) -> None:
            self.query_embedding: list[float] | None = None

        def cosine_distance(self, query_embedding: list[float]) -> FakeDistance:
            self.query_embedding = query_embedding
            return FakeDistance()

        def is_not(self, value: None) -> tuple[str, None]:
            return ("is_not", value)

    class FakeStatement:
        def __init__(self, *selected: object) -> None:
            self.selected = selected
            self.where_clause: object | None = None
            self.order_by_clause: object | None = None
            self.limit_value: int | None = None

        def where(self, clause: object) -> "FakeStatement":
            self.where_clause = clause
            return self

        def order_by(self, clause: object) -> "FakeStatement":
            self.order_by_clause = clause
            return self

        def limit(self, value: int) -> "FakeStatement":
            self.limit_value = value
            return self

    class FakeExecuteResult:
        def __init__(self, rows: list[tuple[Candidate, float]]) -> None:
            self.rows = rows

        def all(self) -> list[tuple[Candidate, float]]:
            return self.rows

    class FakeSession:
        def __init__(self, rows: list[tuple[Candidate, float]]) -> None:
            self.rows = rows
            self.statement: FakeStatement | None = None

        def execute(self, statement: FakeStatement) -> FakeExecuteResult:
            self.statement = statement
            return FakeExecuteResult(self.rows)

    fake_embedding_column = FakeEmbeddingColumn()
    fake_session = FakeSession(
        rows=[
            (
                Candidate(
                    id=1,
                    full_name="Ada Lovelace",
                    email="ada@example.com",
                    phone=None,
                    location="London",
                    summary="Pioneer in computing.",
                    years_experience=5,
                ),
                0.25,
            ),
            (
                Candidate(
                    id=2,
                    full_name="Grace Hopper",
                    email="grace@example.com",
                    phone=None,
                    location="New York",
                    summary="Computer scientist and naval officer.",
                    years_experience=8,
                ),
                0.5,
            ),
        ]
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(candidate_routes, "generate_text_embedding", lambda _: [0.1, 0.2, 0.3])
    monkeypatch.setattr(candidate_routes, "select", lambda *selected: FakeStatement(*selected))
    monkeypatch.setattr(Candidate, "embedding", fake_embedding_column, raising=False)
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        with TestClient(app) as client:
            response = client.post(
                "/candidates/search",
                json={"query_text": "Find strong backend engineers", "limit": 2},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "candidate": {
                    "id": 1,
                    "full_name": "Ada Lovelace",
                    "email": "ada@example.com",
                    "phone": None,
                    "location": "London",
                    "summary": "Pioneer in computing.",
                    "years_experience": 5.0,
                },
                "similarity_score": 0.8,
            },
            {
                "candidate": {
                    "id": 2,
                    "full_name": "Grace Hopper",
                    "email": "grace@example.com",
                    "phone": None,
                    "location": "New York",
                    "summary": "Computer scientist and naval officer.",
                    "years_experience": 8.0,
                },
                "similarity_score": 1 / 1.5,
            },
        ]
    }
    assert fake_embedding_column.query_embedding == [0.1, 0.2, 0.3]
    assert fake_session.statement is not None
    assert fake_session.statement.limit_value == 2
