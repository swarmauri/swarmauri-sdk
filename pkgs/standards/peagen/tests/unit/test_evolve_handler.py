import pytest

from peagen.handlers import evolve_handler as handler
from peagen.handlers import fanout as fanout_mod


@pytest.mark.unit
@pytest.mark.asyncio
async def test_evolve_handler_dispatches(monkeypatch, tmp_path):
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

    monkeypatch.setattr(fanout_mod, "httpx", type("X", (), {"AsyncClient": DummyClient}))

    spec = tmp_path / "evolve.yaml"
    spec.write_text("""MUTATIONS:\n- workspace_uri: ws1\n  target_file: t1\n  import_path: m1\n  entry_fn: f1\n- workspace_uri: ws2\n  target_file: t2\n  import_path: m2\n  entry_fn: f2\n""")

    task = {"id": "T0", "pool": "default", "payload": {"args": {"evolve_spec": str(spec)}}}
    result = await handler.evolve_handler(task)

    assert len(sent) == 4
    assert sent[-1]["method"] == "Work.finished"
    assert result["children"] and len(result["children"]) == 2
