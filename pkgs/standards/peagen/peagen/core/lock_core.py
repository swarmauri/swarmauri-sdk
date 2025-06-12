"""Utilities for locking plan files with a stable hash."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Union

import yaml


def _hash_bytes(data: bytes) -> str:
    """Return a SHA256 hex digest for *data*."""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def lock_plan(plan: Union[str, Path, Dict[str, Any]]) -> str:
    """Return a lock hash for a DOE, evaluation, evolve, or analysis plan.

    Args:
        plan: File path or mapping representing the plan contents.

    Returns:
        str: SHA256 hex digest of the plan.
    """
    if isinstance(plan, (str, Path)):
        text = Path(plan).expanduser().read_text(encoding="utf-8")
    else:
        text = yaml.safe_dump(plan, sort_keys=True)
    return _hash_bytes(text.encode("utf-8"))
