from __future__ import annotations

import json
from pathlib import Path
from peagen.models import TaskRun

class LocalFsResultBackend:
    """Persist TaskRun rows as JSON files in a local directory."""

    def __init__(self, root_dir: str = "./task_runs", **_: object) -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def store(self, task_run: TaskRun) -> None:
        path = self.root / f"{task_run.id}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(task_run.to_dict(), fh, default=str)
