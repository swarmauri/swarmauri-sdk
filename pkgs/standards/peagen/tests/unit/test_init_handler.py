import pytest
from pathlib import Path

from peagen.handlers import init_handler as handler
from peagen.core import init_core
from peagen.cli.task_helpers import build_task
from peagen.orm import Action
from uuid import uuid4


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
        action=Action.VALIDATE,
        args=args,
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
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
                action=Action.VALIDATE,
                args={},
                tenant_id=str(uuid4()),
                pool_id=str(uuid4()),
                repo="repo",
                ref="HEAD",
            )
        )

    with pytest.raises(ValueError):
        await handler.init_handler(
            build_task(
                action=Action.VALIDATE,
                args={"kind": "unknown"},
                tenant_id=str(uuid4()),
                pool_id=str(uuid4()),
                repo="repo",
                ref="HEAD",
            )
        )
