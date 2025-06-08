import pytest
from peagen.models import Task, TaskRun


@pytest.mark.unit
def test_task_dump_roundtrip():
    task = Task(
        pool="p",
        payload={},
        deps=["a"],
        edge_pred="pred",
        labels=["x"],
        config_toml="[tool]"
    )
    blob = task.model_dump_json()
    restored = Task.model_validate_json(blob)
    assert restored.deps == ["a"]
    assert restored.edge_pred == "pred"
    assert restored.labels == ["x"]
    assert restored.config_toml == "[tool]"


@pytest.mark.unit
def test_taskrun_from_task_populates_fields():
    task = Task(
        pool="p",
        payload={},
        deps=["d1", "d2"],
        edge_pred="edge",
        labels=["l"],
        config_toml="cfg"
    )
    tr = TaskRun.from_task(task)
    assert tr.deps == ["d1", "d2"]
    assert tr.edge_pred == "edge"
    assert tr.labels == ["l"]
    assert tr.config_toml == "cfg"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_save_load_preserves_metadata(monkeypatch):
    import importlib
    from peagen.plugins import PluginManager
    from peagen.plugins.queues import InMemoryQueue

    class DummyBackend:
        async def store(self, *args, **kwargs):
            pass

    orig_get = PluginManager.get

    def fake_get(self, group: str, name=None):
        if group == "queues":
            return InMemoryQueue()
        if group == "result_backends":
            return DummyBackend()
        return orig_get(self, group, name)

    monkeypatch.setattr(PluginManager, "get", fake_get)

    gateway = importlib.import_module("peagen.gateway.__init__")
    monkeypatch.setattr(gateway, "queue", InMemoryQueue())

    task = Task(
        pool="p",
        payload={},
        deps=["d"],
        edge_pred="edge",
        labels=["lab"],
        config_toml="cfg",
    )

    await gateway._save_task(task)
    loaded = await gateway._load_task(task.id)

    assert loaded.deps == ["d"]
    assert loaded.edge_pred == "edge"
    assert loaded.labels == ["lab"]
    assert loaded.config_toml == "cfg"
