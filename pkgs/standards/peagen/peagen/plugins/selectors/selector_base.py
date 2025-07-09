from __future__ import annotations

from typing import Any, Dict, List

from peagen.orm import Status
# from peagen.plugins.result_backends import ResultBackendBase


class SelectorBase:
    """Common candidate selection logic."""

    def __init__(self, backend, num_candidates: int = 1) -> None:
        self.backend = backend
        self.num_candidates = num_candidates

    # ---------------------------------------------------------------
    async def get_tasks(self) -> List[Dict[str, Any]]:
        return await self.backend.list_tasks()

    async def get_leader(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        successes = [t for t in tasks if t.get("status") == Status.success.value]
        if successes:
            successes.sort(key=lambda d: d.get("result", {}).get("score", float("inf")))
            return successes[0]
        return None

    async def get_running_candidates(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        running = [t for t in tasks if t.get("status") == Status.running.value]
        running.sort(key=lambda d: str(d.get("date_created") or ""))
        return running[: self.num_candidates]

    async def select(self) -> Dict[str, Any]:
        tasks = await self.get_tasks()
        leader = await self.get_leader(tasks)
        candidates = await self.get_running_candidates(tasks)
        return {"leader": leader, "candidates": candidates}
