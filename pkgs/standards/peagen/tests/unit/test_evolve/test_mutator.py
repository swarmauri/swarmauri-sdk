import pytest
from peagen.mutators.mutate_patch import PatchMutator, apply_patch
from peagen.queue.model import Task, TaskKind
from peagen.llm.ensemble import LLMEnsemble


def test_apply_patch_basic():
    src = "def f(x):\n    return x\n"
    diff = "@@ -1,2 +1,2 @@\n def f(x):\n-    return x\n+    return x + 1\n"
    result = apply_patch(src, diff)
    assert result == "def f(x):\n    return x + 1\n"


def test_patch_mutator(monkeypatch):
    parent_src = "def f(x):\n    return x\n"
    diff = "@@ -1,2 +1,2 @@\n def f(x):\n-    return x\n+    return x + 1\n"
    monkeypatch.setattr(LLMEnsemble, "generate", lambda prompt: diff)
    mut = PatchMutator()
    task = Task(TaskKind.MUTATE, "t1", {"parent_src": parent_src, "entry_sig": "f(x)"})
    res = mut.handle(task)
    assert res.status == "ok"
    child = res.data["payload"]["child_src"]
    assert "return x + 1" in child
    assert res.data["requires"] == {"docker", "cpu"}

