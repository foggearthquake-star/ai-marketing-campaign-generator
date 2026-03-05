"""FAISS store placeholders."""


class FaissStore:
    """Placeholder vector store adapter."""

    def add(self, item_id: str, vector: list[float]) -> None:
        """Placeholder add operation."""
        _ = (item_id, vector)

    def search(self, vector: list[float], top_k: int = 5) -> list[str]:
        """Placeholder similarity search."""
        _ = (vector, top_k)
        return []


class FaissVectorStore:
    """In-memory vector store placeholder."""

    def __init__(self) -> None:
        self.items: list[tuple[str, list[float]]] = []

    def add_embeddings(self, chunks: list[str], embeddings: list[list[float]]) -> None:
        """Store aligned chunks and embeddings in memory."""
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            self.items.append((chunk, embedding))
