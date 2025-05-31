from __future__ import annotations

import random
from dataclasses import asdict

from peagen.queue.model import Task, TaskKind, Result
from peagen.llm.ensemble import LLMEnsemble
from peagen.prompt_sampler import PromptSampler
from peagen.mutators.base import Mutator


class PatchMutator(Mutator):
    KIND = TaskKind.MUTATE
    PROVIDES = {"llm", "cpu"}

    def dispatch(self, task: Task) -> bool:  # type: ignore[override]
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:  # type: ignore[override]
        parent_src = task.payload["parent_src"]
        entry_sig = task.payload["entry_sig"]
        inspirations = task.payload.get("inspirations", [])
        prompt = PromptSampler.build_mutate_prompt(parent_src, inspirations, entry_sig)
        diff = LLMEnsemble.generate(prompt)
        try:
            child_src = apply_patch(parent_src, diff)
        except Exception as e:  # pragma: no cover - simple
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
        payload = {
            "parent_src": parent_src,
            "child_src": child_src,
            "entry_sig": entry_sig,
        }
        exec_task = Task(TaskKind.EXECUTE, f"exec-{random.randint(0,999999):06d}", payload, requires={"docker", "cpu"})
        return Result(task.id, "ok", asdict(exec_task))


def apply_patch(src: str, diff: str) -> str:
    """Apply a unified diff to ``src`` and return the patched text."""
    import re

    src_lines = src.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    lines = diff.splitlines()
    idx = 0
    hunk_re = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")
    while idx < len(lines):
        line = lines[idx]
        if not line.startswith("@@"):
            idx += 1
            continue
        m = hunk_re.match(line)
        if not m:
            raise ValueError("bad hunk header")
        old_start = int(m.group(1)) - 1
        idx += 1
        out.extend(src_lines[i:old_start])
        i = old_start
        while idx < len(lines) and not lines[idx].startswith("@@"):
            line = lines[idx]
            if line.startswith("-"):
                i += 1
            elif line.startswith("+"):
                out.append(line[1:] + "\n")
            elif line.startswith(" ") or line == "":
                out.append(src_lines[i])
                i += 1
            idx += 1
    out.extend(src_lines[i:])
    return "".join(out)
