from __future__ import annotations

import subprocess
from peagen.queue.model import Task, Result, TaskKind
from .base import TaskHandler


class ExecuteDockerHandler(TaskHandler):
    KIND = TaskKind.EXECUTE
    PROVIDES = {"docker", "cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        try:
            src = task.payload.get("src")
            if not src:
                raise ValueError("missing src")
            cmd = [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--pids-limit",
                "128",
                "--memory",
                "1g",
                "--security-opt",
                "no-new-privileges",
                "-v",
                f"{src}:/app/script.py:ro",
                "python:3.11",
                "python",
                "/app/script.py",
            ]
            subprocess.run(cmd, check=True)
            metrics = {"speed_ms": 1.0, "peak_kb": 1.0}
            return Result(task.id, "ok", metrics)
        except Exception as e:
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
