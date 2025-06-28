import pytest

from peagen.handlers import evolve_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


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
    spec.write_text(
        "JOBS:\n- workspace_uri: ws\n  target_file: t.py\n  import_path: mod\n  entry_fn: f\noperators:\n  mutation:\n    - kind: echo_mutator\n      probability: 1\n      uri: patch.p\n"
    )

    task = TaskRead.model_construct(
        id="P1",
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="default",
        payload={"args": {"evolve_spec": str(spec)}},
        status=Status.queued,
        note=None,
        spec_hash="",
        date_created=datetime.now(timezone.utc),
        last_modified=datetime.now(timezone.utc),
    )
    result = await handler.evolve_handler(task)

    assert result["jobs"] == 1
    assert sent and sent[-1]["method"] == "Work.finished"
    submit = sent[0]
    assert submit["method"] == "Task.submit"
    assert submit["params"]["payload"]["action"] == "mutate"
    assert submit["params"]["payload"]["args"].get("mutations")
