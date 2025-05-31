from __future__ import annotations

from pathlib import Path

from typing import Set

from peagen.queue.model import Task, Result, TaskKind
from .base import TaskHandlerBase


class PromptSampler:
    @staticmethod
    def build_mutate_prompt(parent_src: str, inspirations: list[str], entry_sig: str) -> str:
        return parent_src + "\n" + "\n".join(inspirations) + "\n" + entry_sig


class LLMEnsemble:
    @staticmethod
    def generate(prompt: str) -> str:
        return prompt  # stub; tests may monkeypatch


class PatchMutatorHandler(TaskHandlerBase):
    KIND: TaskKind = TaskKind.MUTATE
    PROVIDES: Set[str] = {"llm", "cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        parent = task.payload.get("parent_src", "")
        insp = task.payload.get("inspirations", [])
        entry = task.payload.get("entry_sig", "")
        dest = Path(task.payload.get("child_path", "child.py"))
        try:
            prompt = PromptSampler.build_mutate_prompt(parent, insp, entry)
            patch = LLMEnsemble.generate(prompt)
            dest.write_text(patch)
            exec_task = Task(TaskKind.EXECUTE, task.id + "-exec", {"src": str(dest)}, requires={"docker", "cpu"})
            return Result(task.id, "ok", {"execute_task": exec_task.to_dict()})
        except Exception as e:
            retry = isinstance(e, RuntimeError)
            return Result(task.id, "error", {"msg": str(e), "retryable": retry})
