import os
from pathlib import Path

import pytest

from peagen.commands import mutate as mutate_cmd


@pytest.mark.unit
def test_run_mutate_sync(monkeypatch, tmp_path):
    parent = tmp_path / "src.py"
    parent.write_text("def f(x):\n    return x\n")
    out = tmp_path / "child.py"
    diff = "@@ -1,2 +1,2 @@\n def f(x):\n-    return x\n+    return x+1\n"

    monkeypatch.setattr(
        mutate_cmd.PromptSampler,
        "build_mutate_prompt",
        lambda parent_src, insp, entry: "prompt",
    )
    monkeypatch.setattr(
        mutate_cmd.LLMEnsemble,
        "generate",
        lambda prompt, backend=None: diff,
    )

    mutate_cmd.run_mutate(str(parent), "f", str(out), None, False)
    assert out.read_text() == "def f(x):\n    return x+1\n"


@pytest.mark.unit
def test_run_mutate_queue(monkeypatch, tmp_path):
    parent = tmp_path / "src.py"
    parent.write_text("print('hi')\n")
    q = mutate_cmd.make_queue("stub")
    monkeypatch.setattr(mutate_cmd, "make_queue", lambda *a, **k: q)

    mutate_cmd.run_mutate(str(parent), "f", str(tmp_path/"out.py"), None, True)
    task = q.pop(block=False)
    assert task is not None
    assert task.kind == mutate_cmd.TaskKind.MUTATE
    assert task.payload["parent_src"].startswith("print")
