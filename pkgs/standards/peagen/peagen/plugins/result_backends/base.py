from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from peagen.models.task import TaskRun


class ResultBackendBase:
    """Default functionality shared by result backend implementations."""

    async def store(self, task_run: TaskRun) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def list_tasks(self) -> List[Dict[str, Any]]:
        """Return all stored TaskRun objects as dictionaries."""
        out: List[Dict[str, Any]] = []
        if hasattr(self, "tasks"):
            for t in getattr(self, "tasks").values():
                data = t.to_dict() if hasattr(t, "to_dict") else t
                data["id"] = str(data.get("id"))
                if data.get("started_at") is not None:
                    data["started_at"] = str(data["started_at"])
                out.append(data)
            return out
        if hasattr(self, "root"):
            for path in Path(getattr(self, "root")).glob("*.json"):
                try:
                    out.append(json.loads(path.read_text()))
                except Exception:
                    continue
            return out
        return out
