from __future__ import annotations

from typing import Any, Dict

from .result_backend_selector import ResultBackendSelector


class InputSelector(ResultBackendSelector):
    """Gen0 candidate provided by the user."""

    def __init__(
        self, backend: Any, initial_candidate: Dict[str, Any], num_candidates: int = 1
    ) -> None:
        super().__init__(backend, num_candidates)
        self.initial_candidate = initial_candidate
        self._used_input = False

    async def select(self) -> Dict[str, Any]:
        if not self._used_input:
            self._used_input = True
            return {"leader": None, "candidates": [self.initial_candidate]}
        return await super().select()
