"""Helpers for chaining task and artifact hashes."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


def chain_hash(data: bytes, prev_hash: str | None = None) -> str:
    """Return a chained SHA256 hash for *data* and *prev_hash*."""
    h = hashlib.sha256()
    if prev_hash:
        h.update(prev_hash.encode("utf-8"))
    h.update(data)
    return h.hexdigest()


class TaskChainer:
    """Compute chained hashes for tasks and artifacts."""

    def __init__(self, prev_hash: str | None = None) -> None:
        self.prev_hash = prev_hash

    def add_task(self, payload: Dict[str, Any]) -> str:
        """Add a task payload and return the new chain hash."""
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.prev_hash = chain_hash(data, self.prev_hash)
        return self.prev_hash

    def add_artifact(self, artifact_data: bytes) -> str:
        """Add artifact bytes to the chain and return the new hash."""
        self.prev_hash = chain_hash(artifact_data, self.prev_hash)
        return self.prev_hash

    @property
    def current_hash(self) -> Optional[str]:
        """Return the most recent hash in the chain."""
        return self.prev_hash
