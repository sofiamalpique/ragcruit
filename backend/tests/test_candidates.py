from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_candidate_endpoint() -> None:
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
    assert response.json() == {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "phone": "+351123456789",
        "location": "Lisbon",
        "summary": "Pioneer in computing.",
        "years_experience": 5.0,
        "skills": ["python", "machine learning"],
    }
