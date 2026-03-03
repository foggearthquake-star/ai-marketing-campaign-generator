"""Text utility helpers."""


def normalize_text(text: str) -> str:
    """Return a normalized text value."""
    return " ".join(text.split())
