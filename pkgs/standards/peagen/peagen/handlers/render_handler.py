from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

from peagen.queue.model import Task, Result, TaskKind
from .base import TaskHandlerBase


class RenderHandler(TaskHandlerBase):
    """Render Jinja template payload."""

    KIND: TaskKind = TaskKind.RENDER
    PROVIDES: Set[str] = {"cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        tmpl_str = task.payload.get("template", "")
        vars_ = task.payload.get("vars", {})
        dest = task.payload.get("dest")
        try:
            rendered = Template(tmpl_str).render(**vars_)
            if dest:
                Path(dest).write_text(rendered)
            return Result(task.id, "ok", {"rendered": rendered})
        except Exception as e:
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
