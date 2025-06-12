import pytest

from peagen.handlers import evolve_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_evolve_handler_fanout(monkeypatch, tmp_path):
    sent = []

    class DummyClient:
        def __init__(self, *a, **kw):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def post(self, url, json):
            sent.append(json)
            class R:
                def raise_for_status(self):
                    pass
            return R()

    import peagen.handlers.fanout as fanout
    monkeypatch.setattr(fanout, "httpx", type("X", (), {"AsyncClient": DummyClient}))

    spec = tmp_path / "spec.yaml"
    spec.write_text("JOBS:\n- workspace_uri: ws\n  target_file: t.py\n  import_path: mod\n  entry_fn: f\n")

    task = {"id": "P1", "pool": "default", "payload": {"args": {"evolve_spec": str(spec)}}}
    result = await handler.evolve_handler(task)

    assert result["jobs"] == 1
    assert len(sent) == 1
    batch = sent[0]
    assert isinstance(batch, list)
    assert batch[-1]["method"] == "Work.finished"
    submit = batch[0]
    assert submit["method"] == "Task.submit"
    assert "action" not in submit["params"]["payload"]
