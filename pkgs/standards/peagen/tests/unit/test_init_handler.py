import pytest
from pathlib import Path

from peagen.handlers import init_handler as handler
from peagen.core import init_core
from peagen.transport.jsonrpc_schemas.task import SubmitParams, Status


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind, func",
    [
        ("project", "init_project"),
        ("template-set", "init_template_set"),
        ("doe-spec", "init_doe_spec"),
        ("ci", "init_ci"),
    ],
)
async def test_init_handler_dispatch(monkeypatch, kind, func):
    called = {}

    def fake(**kwargs):
        called.update(kwargs)
        return {"kind": kind}

    monkeypatch.setattr(init_core, func, fake)
    args = {"kind": kind, "path": "~/p"}
    task = SubmitParams(
        id="1", pool="default", payload={"args": args}, status=Status.waiting
    )
    result = await handler.init_handler(task)

    assert result == {"kind": kind}
    assert called.get("path") == Path("~/p").expanduser()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_init_handler_errors(monkeypatch):
    with pytest.raises(ValueError):
        task = SubmitParams(
            id="1", pool="default", payload={"args": {}}, status=Status.waiting
        )
        await handler.init_handler(task)

    with pytest.raises(ValueError):
        task = SubmitParams(
            id="1",
            pool="default",
            payload={"args": {"kind": "unknown"}},
            status=Status.waiting,
        )
        await handler.init_handler(task)
