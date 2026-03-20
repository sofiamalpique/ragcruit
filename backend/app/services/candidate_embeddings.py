from openai import OpenAI

import app.core.config as config
from app.models.candidate import Candidate
from app.services.candidate_embedding_text import build_candidate_embedding_text


def generate_candidate_embedding(candidate: Candidate) -> list[float]:
    if not config.openai_api_key:
        raise RuntimeError(
            "Candidate embedding generation requires OPENAI_API_KEY to be set."
        )

    client = OpenAI(api_key=config.openai_api_key)
    candidate_text = build_candidate_embedding_text(candidate)
    response = client.embeddings.create(
        model=config.openai_embedding_model,
        input=candidate_text,
        encoding_format="float",
    )

    return response.data[0].embedding
