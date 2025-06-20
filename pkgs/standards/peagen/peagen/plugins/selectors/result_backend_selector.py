from __future__ import annotations

from typing import Any

from .selector_base import SelectorBase


class ResultBackendSelector(SelectorBase):
    """Select candidates based on the results backend."""

    def __init__(self, backend: Any, num_candidates: int = 1) -> None:
        super().__init__(backend, num_candidates)
