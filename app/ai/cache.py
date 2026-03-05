"""In-memory AI response cache."""

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


class AICache:
    """Simple prompt-hash based in-memory cache."""

    _store: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _key(prompt: str) -> str:
        return sha256(prompt.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, prompt: str) -> dict | str | None:
        """Return cached response payload for prompt if available."""
        key = cls._key(prompt)
        payload = cls._store.get(key)
        if payload is None:
            return None
        return payload.get("response")

    @classmethod
    def set(cls, prompt: str, result: dict | str | None) -> None:
        """Store response payload in cache."""
        key = cls._key(prompt)
        cls._store[key] = {
            "prompt": prompt,
            "response": result,
            "created_at": datetime.now(timezone.utc),
        }
