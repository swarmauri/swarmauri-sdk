import pytest

from peagen.handlers import sort_handler as handler_module


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_handler_single_project(monkeypatch):
    called = {}

    def fake_single(params):
        called["single"] = True
        return {"sorted": []}

    def fake_all(params):
        called["all"] = True
        return {"sorted_all_projects": {}}

    monkeypatch.setattr(handler_module, "sort_single_project", fake_single)
    monkeypatch.setattr(handler_module, "sort_all_projects", fake_all)
    monkeypatch.setattr(handler_module, "_merge_cli_into_toml", lambda **k: {"project_name": "demo"})

    task = {"payload": {"args": {"projects_payload": "p.yaml"}}}
    await handler_module.sort_handler(task)
    assert called.get("single") is True
    assert called.get("all") is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_handler_all_projects(monkeypatch):
    called = {}

    def fake_single(params):
        called.setdefault("single", 0)
        called["single"] += 1
        return {"sorted": []}

    def fake_all(params):
        called["all"] = True
        return {"sorted_all_projects": {}}

    monkeypatch.setattr(handler_module, "sort_single_project", fake_single)
    monkeypatch.setattr(handler_module, "sort_all_projects", fake_all)
    monkeypatch.setattr(handler_module, "_merge_cli_into_toml", lambda **k: {"project_name": None})

    task = {"payload": {"args": {"projects_payload": "p.yaml"}}}
    await handler_module.sort_handler(task)
    assert called.get("all") is True
