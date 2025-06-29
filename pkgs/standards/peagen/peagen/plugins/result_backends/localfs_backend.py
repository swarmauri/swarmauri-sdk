from __future__ import annotations

import json
from pathlib import Path
from peagen.orm import TaskRunModel
from .base import ResultBackendBase


class LocalFsResultBackend(ResultBackendBase):
    """Persist TaskRun rows as JSON files in a local directory."""

    def __init__(self, root_dir: str = "./task_runs", **_: object) -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def store(self, task_run: TaskRunModel) -> None:
        path = self.root / f"{task_run.id}.json"
        with path.open("w", encoding="utf-8") as fh:
            from peagen.schemas import TaskRunRead

            data = TaskRunRead.model_validate(task_run).model_dump()
            json.dump(data, fh, default=str)
