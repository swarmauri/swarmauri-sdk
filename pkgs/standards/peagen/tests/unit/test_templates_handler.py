import pytest

from peagen.handlers import templates_handler as handler
from peagen.cli.task_helpers import build_task


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

    payload = {"action": op, **args}
    task = build_task(
        action="templates",
        args=payload,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.templates_handler(task)

    assert result == {"op": op}
    assert called
