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
