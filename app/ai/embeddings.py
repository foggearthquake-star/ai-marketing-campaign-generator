"""Embeddings helpers."""

from openai import OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_BASE_URL

EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text chunks."""
    if not texts:
        return []
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    # Keep output aligned with input length and avoid empty-string API edge cases.
    normalized_texts = [text if text and text.strip() else " " for text in texts]
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=normalized_texts,
    )
    return [item.embedding for item in response.data]
