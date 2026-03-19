from sqlalchemy import delete, select
from fastapi.testclient import TestClient

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
