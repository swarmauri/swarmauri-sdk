import pytest

from peagen.handlers import doe_process_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_doe_process_handler_dispatches(monkeypatch, tmp_path):
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

    def fake_generate_payload(**kwargs):
        p = tmp_path / "out.yaml"
        p.write_text("PROJECTS:\n- NAME: A\n- NAME: B\n")
        return {"output": str(p)}

    monkeypatch.setattr(handler, "generate_payload", fake_generate_payload)

    task = {"id": "T0", "pool": "default", "payload": {"args": {"spec": "s", "template": "t", "output": str(tmp_path / "out.yaml")}}}
    result = await handler.doe_process_handler(task)

    assert len(sent) == 1
    batch = sent[0]
    assert isinstance(batch, list)
    assert batch[-1]["method"] == "Work.finished"
    assert batch[-1]["params"]["status"] == "waiting"
    submits = [req for req in batch if req.get("method") == "Task.submit"]
    assert len(submits) == 2
    assert result["children"] and len(result["children"]) == 2
