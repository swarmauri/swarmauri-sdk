import os
import types
import importlib.metadata as im

import pytest

from peagen.handlers import (
    RenderHandler,
    PatchMutatorHandler,
    ExecuteDockerHandler,
    ExecuteGPUHandler,
    EvaluateHandler,
    can_handle,
)
from peagen.task_model import Task, Result, TaskKind
from peagen.plugin_registry import registry, discover_and_register_plugins
from peagen.worker import InlineWorker
from peagen.queue.stub_queue import StubQueue


@pytest.mark.unit
def test_render_handler(tmp_path):
    task = Task(TaskKind.RENDER, "t1", {"template": "hi {{name}}", "vars": {"name": "x"}, "dest": str(tmp_path / "out.txt")})
    h = RenderHandler()
    res = h.handle(task)
    assert res.status == "ok"


@pytest.mark.unit
def test_mutator_handler(monkeypatch, tmp_path):
    def fake_prompt(parent, insp, entry):
        return "prompt"
    def fake_generate(prompt):
        return "child src"
    monkeypatch.setattr(PatchMutatorHandler, "PROVIDES", {"llm", "cpu"})
    monkeypatch.setattr("peagen.handlers.mutate_patch.PromptSampler.build_mutate_prompt", fake_prompt)
    monkeypatch.setattr("peagen.handlers.mutate_patch.LLMEnsemble.generate", lambda p: "child")
    task = Task(TaskKind.MUTATE, "m1", {"parent_src": "p", "child_path": str(tmp_path/"c.py")})
    h = PatchMutatorHandler()
    res = h.handle(task)
    assert res.status == "ok"
    assert res.data["execute_task"]["kind"] == "execute"


@pytest.mark.unit
def test_execute_handlers():
    task = Task(TaskKind.EXECUTE, "e1", {})
    assert ExecuteDockerHandler().handle(task).status == "ok"
    assert ExecuteGPUHandler().handle(task).status == "ok"


@pytest.mark.unit
def test_evaluate_handler():
    task = Task(TaskKind.EVALUATE, "ev1", {"score": 5})
    res = EvaluateHandler().handle(task)
    assert res.status == "ok" and res.data["score"] == 5.0


@pytest.mark.unit
def test_plugin_discovery_and_allowlist(monkeypatch):
    registry.clear()
    ep = im.EntryPoint("render", "peagen.handlers.render_handler:RenderHandler", "peagen.task_handlers")
    def fake_entry_points(group):
        if group == "peagen.task_handlers":
            return [ep]
        return []
    monkeypatch.setattr(im, "entry_points", fake_entry_points)
    discover_and_register_plugins()
    assert "render" in registry["task_handlers"]
    os.environ["WORKER_PLUGINS"] = "RenderHandler"
    q = StubQueue()
    worker = InlineWorker(q, caps={"cpu"})
    names = [h.__class__.__name__ for h in worker.handlers]
    assert names == ["RenderHandler"]


@pytest.mark.unit
def test_can_handle_helper():
    task = Task(TaskKind.RENDER, "t", {}, requires={"cpu"})
    assert can_handle(task, RenderHandler, {"cpu"})
    assert not can_handle(task, ExecuteGPUHandler, {"cpu"})
