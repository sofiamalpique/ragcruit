from fastapi.testclient import TestClient
from sqlalchemy import delete, select

import app.api.routes.jobs as job_routes
from app.db.session import SessionLocal
from app.db.session import get_db_session
from app.main import app
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting


def test_job_posting_endpoints() -> None:
    with TestClient(app) as client:
        with SessionLocal() as session:
            session.execute(delete(JobPosting))
            session.commit()

        create_response = client.post(
            "/jobs",
            json={
                "title": "Backend Engineer",
                "company_name": "Ragcruit",
                "location": "Lisbon",
                "description": "Build backend systems for candidate search.",
                "requirements": "Python, FastAPI, PostgreSQL",
                "min_years_experience": 3,
            },
        )

        assert create_response.status_code == 201
        create_response_data = create_response.json()
        assert create_response_data == {
            "id": create_response_data["id"],
            "title": "Backend Engineer",
            "company_name": "Ragcruit",
            "location": "Lisbon",
            "description": "Build backend systems for candidate search.",
            "requirements": "Python, FastAPI, PostgreSQL",
            "min_years_experience": 3.0,
        }

        list_response = client.get("/jobs")
        assert list_response.status_code == 200
        assert list_response.json() == [create_response_data]

        get_response = client.get(f"/jobs/{create_response_data['id']}")
        assert get_response.status_code == 200
        assert get_response.json() == create_response_data

    with SessionLocal() as session:
        stored_job_posting = session.scalar(
            select(JobPosting).where(JobPosting.id == create_response_data["id"])
        )

    assert stored_job_posting is not None
    assert stored_job_posting.title == "Backend Engineer"
    assert stored_job_posting.company_name == "Ragcruit"


def test_match_candidates_to_job_posting_endpoint(monkeypatch) -> None:
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
        def __init__(
            self,
            job_posting: JobPosting,
            rows: list[tuple[Candidate, float]],
        ) -> None:
            self.job_posting = job_posting
            self.rows = rows
            self.statement: FakeStatement | None = None

        def get(self, model: type[JobPosting], job_posting_id: int) -> JobPosting | None:
            if model is JobPosting and job_posting_id == self.job_posting.id:
                return self.job_posting
            return None

        def execute(self, statement: FakeStatement) -> FakeExecuteResult:
            self.statement = statement
            return FakeExecuteResult(self.rows)

    fake_candidate_embedding_column = FakeEmbeddingColumn()
    job_posting = JobPosting(
        id=10,
        title="Machine Learning Engineer",
        company_name="Ragcruit",
        location="Remote",
        description="Build matching systems.",
        requirements="Python and embeddings experience",
        min_years_experience=4,
    )
    job_posting.embedding = [0.4, 0.5, 0.6]
    fake_session = FakeSession(
        job_posting=job_posting,
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
                0.2,
            ),
            (
                Candidate(
                    id=2,
                    full_name="Grace Hopper",
                    email="grace@example.com",
                    phone=None,
                    location="REMOTE",
                    summary="Computer scientist and naval officer.",
                    years_experience=8,
                ),
                0.4,
            ),
        ],
    )

    def override_get_db_session():
        yield fake_session

    monkeypatch.setattr(job_routes, "select", lambda *selected: FakeStatement(*selected))
    monkeypatch.setattr(Candidate, "embedding", fake_candidate_embedding_column, raising=False)
    monkeypatch.setattr(JobPosting, "embedding", object(), raising=False)
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        with TestClient(app) as client:
            response = client.post("/jobs/10/match", json={"limit": 2})
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
                "similarity_score": 1 / 1.2,
                "relevance_score": 1 / 1.2 + 0.1,
                "match_reasons": [
                    "Strong semantic match to the job description",
                    "Experience meets the minimum requirement",
                ],
            },
            {
                "candidate": {
                    "id": 2,
                    "full_name": "Grace Hopper",
                    "email": "grace@example.com",
                    "phone": None,
                    "location": "REMOTE",
                    "summary": "Computer scientist and naval officer.",
                    "years_experience": 8.0,
                },
                "similarity_score": 1 / 1.4,
                "relevance_score": 1 / 1.4 + 0.1 + 0.05,
                "match_reasons": [
                    "Semantic match to the job description",
                    "Experience meets the minimum requirement",
                    "Location matches the job posting",
                ],
            },
        ]
    }
    assert fake_candidate_embedding_column.query_embedding == [0.4, 0.5, 0.6]
    assert fake_session.statement is not None
    assert fake_session.statement.limit_value == 2
