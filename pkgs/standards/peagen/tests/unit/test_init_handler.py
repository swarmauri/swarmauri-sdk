import pytest
from pathlib import Path

from peagen.handlers import init_handler as handler, ensure_task
from peagen.core import init_core


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
    result = await handler.init_handler(ensure_task({"payload": {"args": args}}))

    assert result == {"kind": kind}
    assert called.get("path") == Path("~/p").expanduser()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_init_handler_errors(monkeypatch):
    with pytest.raises(ValueError):
        await handler.init_handler(ensure_task({"payload": {"args": {}}}))

    with pytest.raises(ValueError):
        await handler.init_handler(
            ensure_task({"payload": {"args": {"kind": "unknown"}}})
        )
