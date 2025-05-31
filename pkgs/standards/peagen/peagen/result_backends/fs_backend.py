from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .base import ResultBackendBase
from peagen.queue.model import Result, TaskKind


class FSBackend(ResultBackendBase):
    """Filesystem-backed result store."""

    def __init__(self, root: str = ".peagen/results", compress: bool = False) -> None:
        self._root = Path(root).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self.compress = compress

    def _path(self, result: Result) -> Path:
        date = result.created_at.split("T")[0]
        folder = self._root / date
        folder.mkdir(parents=True, exist_ok=True)
        fname = f"{result.task_id}.msgpack"
        return folder / fname

    def save(self, result: Result) -> None:
        path = self._path(result)
        tmp = path.with_suffix(".tmp")
        data = json.dumps(asdict(result))
        tmp.write_text(data, encoding="utf-8")
        os.replace(tmp, path)

    def get(self, task_id: str) -> Result | None:
        for day in self._root.iterdir():
            file = day / f"{task_id}.msgpack"
            if file.exists():
                data = json.loads(file.read_text("utf-8"))
                return Result(**data)
        return None

    def iter(self, kind: TaskKind | None = None) -> Iterable[Result]:
        for day in sorted(self._root.iterdir()):
            for file in day.glob("*.msgpack"):
                data = json.loads(file.read_text("utf-8"))
                res = Result(**data)
                if kind is None or data.get("kind") == kind:
                    yield res
