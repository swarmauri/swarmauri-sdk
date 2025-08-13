import pytest
from pathlib import Path

from peagen.handlers import init_handler as handler
from peagen.core import init_core
from peagen.cli.task_helpers import build_task


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
    task = build_task(
        action="init",
        args=args,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.init_handler(task)

    assert result == {"kind": kind}
    assert called.get("path") == Path("~/p").expanduser()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_init_handler_errors(monkeypatch):
    with pytest.raises(ValueError):
        await handler.init_handler(
            build_task(
                action="init",
                args={},
                pool_id="p",
                repo="repo",
                ref="HEAD",
            )
        )

    with pytest.raises(ValueError):
        await handler.init_handler(
            build_task(
                action="init",
                args={"kind": "unknown"},
                pool_id="p",
                repo="repo",
                ref="HEAD",
            )
        )
