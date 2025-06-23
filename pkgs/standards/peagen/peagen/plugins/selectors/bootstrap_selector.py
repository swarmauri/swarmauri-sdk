from __future__ import annotations

from typing import Any, Dict, List

from .result_backend_selector import ResultBackendSelector


class BootstrapSelector(ResultBackendSelector):
    """Gen0 candidates come from a bootstrap list."""

    def __init__(
        self, backend: Any, bootstrap: List[Dict[str, Any]], num_candidates: int = 1
    ) -> None:
        super().__init__(backend, num_candidates)
        self.bootstrap = bootstrap
        self._used_bootstrap = False

    async def select(self) -> Dict[str, Any]:
        if not self._used_bootstrap:
            self._used_bootstrap = True
            return {"leader": None, "candidates": self.bootstrap}
        return await super().select()
