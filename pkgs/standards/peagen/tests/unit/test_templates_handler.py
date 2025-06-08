import pytest

from peagen.handlers import templates_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "op, func, args",
    [
        ("list", "list_template_sets", {}),
        ("show", "show_template_set", {"name": "n"}),
        ("add", "add_template_set", {"source": "src", "from_bundle": None, "editable": False, "force": False}),
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

    result = await handler.templates_handler({"payload": {"args": {"operation": op, **args}}})

    assert result == {"op": op}
    assert called
