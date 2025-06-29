import pytest

from peagen.handlers import doe_process_handler as handler
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT, TASK_PATCH
from peagen.defaults import WORK_FINISHED


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

    class DummyPM:
        def __init__(self, cfg):
            pass

        def get(self, name):
            return DummyAdapter()

    class DummyAdapter:
        root_uri = "file://dummy/"

        def upload(self, key, fh):
            return f"{self.root_uri}{key}"

    monkeypatch.setattr(handler, "PluginManager", DummyPM)
    monkeypatch.setattr(handler, "FileStorageAdapter", DummyAdapter)
    monkeypatch.setattr(handler, "resolve_cfg", lambda toml_path=".peagen.toml": {})

    def fake_generate_payload(**kwargs):
        p1 = tmp_path / "out_0.yaml"
        p2 = tmp_path / "out_1.yaml"
        p1.write_text("PROJECTS:\n- NAME: A\n")
        p2.write_text("PROJECTS:\n- NAME: B\n")
        return {"outputs": [str(p1), str(p2)]}

    monkeypatch.setattr(handler, "generate_payload", fake_generate_payload)

    task = {
        "id": "T0",
        "pool": "default",
        "payload": {
            "args": {"spec": "s", "template": "t", "output": str(tmp_path / "out.yaml")}
        },
    }
    result = await handler.doe_process_handler(task)

    assert len(sent) == 4
    assert sent[0]["method"] == TASK_SUBMIT
    assert sent[1]["method"] == TASK_SUBMIT
    assert sent[2]["method"] == TASK_PATCH
    assert sent[-1]["method"] == WORK_FINISHED
    assert sent[-1]["params"]["status"] == "waiting"
    assert result["children"] and len(result["children"]) == 2
    assert result["outputs"][0].startswith("PROJECTS:")
    assert sent[0]["params"]["payload"]["args"]["projects_payload"].startswith(
        "PROJECTS:"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_doe_process_handler_dry_run(monkeypatch, tmp_path):
    sent = []

    class DummyClient:
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

    class DummyPM:
        def __init__(self, cfg):
            pass

        def get(self, name):
            return DummyAdapter()

    class DummyAdapter:
        root_uri = "file://dummy/"

        def upload(self, key, fh):
            return f"{self.root_uri}{key}"

    monkeypatch.setattr(handler, "PluginManager", DummyPM)
    monkeypatch.setattr(handler, "FileStorageAdapter", DummyAdapter)
    monkeypatch.setattr(handler, "resolve_cfg", lambda toml_path=".peagen.toml": {})

    def fake_generate_payload(**kwargs):
        p1 = tmp_path / "out_0.yaml"
        return {
            "outputs": [str(p1)],
            "artifact_outputs": [],
            "evaluations": [],
            "count": 1,
            "bytes": 0,
            "llm_keys": [],
            "other_keys": [],
            "dry_run": True,
        }

    monkeypatch.setattr(handler, "generate_payload", fake_generate_payload)

    task = {
        "id": "T0",
        "pool": "default",
        "payload": {
            "args": {
                "spec": "s",
                "template": "t",
                "output": str(tmp_path / "out.yaml"),
                "dry_run": True,
            }
        },
    }
    result = await handler.doe_process_handler(task)

    assert sent == []
    assert result["children"] == []
    assert result["_final_status"] == "success"
