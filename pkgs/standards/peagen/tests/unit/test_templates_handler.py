import pytest

from peagen.handlers import templates_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "op, func, args",
    [
        ("list", "list_template_sets", {}),
        ("show", "show_template_set", {"name": "n"}),
        (
            "add",
            "add_template_set",
            {"source": "src", "from_bundle": None, "editable": False, "force": False},
        ),
        ("remove", "remove_template_set", {"name": "n"}),
    ],
)
async def test_templates_handler_dispatch(monkeypatch, op, func, args):
    called = {}

    def fake(*a, **kw):
        called["args"] = a
        called["kwargs"] = kw
        return {"op": op}

    monkeypatch.setattr(handler, func, fake)

    task = TaskRead.model_construct(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="default",
        payload={"args": {"operation": op, **args}},
        status=Status.queued,
        note=None,
        spec_hash="",
        date_created=datetime.now(timezone.utc),
        last_modified=datetime.now(timezone.utc),
    )
    result = await handler.templates_handler(task)

    assert result == {"op": op}
    assert called
