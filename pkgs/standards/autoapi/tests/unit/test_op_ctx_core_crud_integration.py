import pytest
from sqlalchemy import Column, Integer

from autoapi.v3 import Base, op_ctx
import autoapi.v3.core as core


CANONICAL_VERBS = ["create", "read", "update", "delete"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb, alias_kw, handler_alias",
    [
        *((v, None, v) for v in CANONICAL_VERBS),
        *((v, v, v) for v in CANONICAL_VERBS),
        *((v, f"alt_{v}", f"alt_{v}") for v in CANONICAL_VERBS),
    ],
)
async def test_op_ctx_target_core_executes(monkeypatch, verb, alias_kw, handler_alias):
    Base.metadata.clear()
    calls = []

    async def fake_core(*_args, **_kwargs):
        calls.append("core")
        return {"verb": verb}

    monkeypatch.setattr(core, verb, fake_core)

    deco = {"target": verb}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Widget(Base):
        __tablename__ = f"widgets_{verb}_{handler_alias}"
        id = Column(Integer, primary_key=True)

        @op_ctx(**deco)
        def op(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            return {"verb": "custom"}

    ctx = {"path_params": {"id": 1}, "db": object(), "body": {"id": 1}}
    ctx_before = ctx.copy()
    handler = getattr(Widget.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"verb": verb}
    assert calls == ["core"]
    assert ctx == ctx_before
    assert hasattr(Widget.handlers, handler_alias)


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", CANONICAL_VERBS)
async def test_op_ctx_alias_overrides_core(monkeypatch, verb):
    Base.metadata.clear()
    calls = []

    async def fake_core(*_args, **_kwargs):
        calls.append("core")
        return {"verb": verb}

    monkeypatch.setattr(core, verb, fake_core)

    class Gadget(Base):
        __tablename__ = f"gadgets_custom_{verb}"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias=verb)
        def custom(cls, ctx):
            calls.append("custom")
            return {"verb": "custom"}

    ctx = {"path_params": {"id": 1}, "db": object(), "body": {"id": 1}}
    ctx_before = ctx.copy()
    result = await getattr(Gadget.handlers, verb).raw(ctx)
    assert result == {"verb": "custom"}
    assert calls == ["custom"]
    assert ctx == ctx_before
    assert hasattr(Gadget.handlers, verb)
    assert not hasattr(Gadget.handlers, "custom")
