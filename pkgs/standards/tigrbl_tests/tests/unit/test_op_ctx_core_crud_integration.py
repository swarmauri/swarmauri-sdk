import pytest
from sqlalchemy import Column, Integer, String

from tigrbl import Base, op_ctx
import tigrbl.core as core


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "alias_kw, handler_alias",
    [(None, "read"), ("read", "read"), ("fetch", "fetch")],
)
async def test_op_ctx_target_read_core_executes(monkeypatch, alias_kw, handler_alias):
    Base.metadata.clear()
    storage = {1: {"id": 1}}
    calls = []

    async def fake_read(model, ident, db=None):
        calls.append("core")
        return storage[ident]

    monkeypatch.setattr(core, "read", fake_read)

    deco = {"target": "read"}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Widget(Base):
        __tablename__ = f"widgets_{handler_alias}"
        id = Column(Integer, primary_key=True)

        @op_ctx(**deco)
        def read(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "db": object()}
    ctx_before = ctx.copy()
    handler = getattr(Widget.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"id": 1}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1}}
    assert calls == ["core"]


@pytest.mark.asyncio
async def test_op_ctx_alias_read_overrides_core(monkeypatch):
    Base.metadata.clear()
    storage = {1: {"id": 1}}
    calls = []

    async def fake_read(model, ident, db=None):
        calls.append("core")
        return storage[ident]

    monkeypatch.setattr(core, "read", fake_read)

    class Gadget(Base):
        __tablename__ = "gadgets_custom_read"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias="read")
        def custom(cls, ctx):
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "db": object()}
    ctx_before = ctx.copy()
    result = await Gadget.handlers.read.raw(ctx)
    assert result == {"id": 99}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1}}
    assert calls == ["custom"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "alias_kw, handler_alias",
    [(None, "create"), ("create", "create"), ("make", "make")],
)
async def test_op_ctx_target_create_core_executes(monkeypatch, alias_kw, handler_alias):
    Base.metadata.clear()
    storage = {}
    calls = []

    async def fake_create(model, data, db=None):
        calls.append("core")
        storage[data["id"]] = data.copy()
        return data

    monkeypatch.setattr(core, "create", fake_create)

    deco = {"target": "create"}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Gadget(Base):
        __tablename__ = f"gadgets_create_{handler_alias}"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(**deco)
        def create(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"payload": {"id": 1, "value": "a"}, "db": object()}
    ctx_before = ctx.copy()
    handler = getattr(Gadget.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"id": 1, "value": "a"}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1, "value": "a"}}
    assert calls == ["core"]


@pytest.mark.asyncio
async def test_op_ctx_alias_create_overrides_core(monkeypatch):
    Base.metadata.clear()
    storage = {}
    calls = []

    async def fake_create(model, data, db=None):
        calls.append("core")
        storage[data["id"]] = data.copy()
        return data

    monkeypatch.setattr(core, "create", fake_create)

    class Widget(Base):
        __tablename__ = "widgets_custom_create"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(alias="create")
        def custom(cls, ctx):
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"payload": {"id": 1, "value": "a"}, "db": object()}
    ctx_before = ctx.copy()
    result = await Widget.handlers.create.raw(ctx)
    assert result == {"id": 99}
    assert ctx == ctx_before
    assert storage == {}
    assert calls == ["custom"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "alias_kw, handler_alias",
    [(None, "update"), ("update", "update"), ("modify", "modify")],
)
async def test_op_ctx_target_update_core_executes(monkeypatch, alias_kw, handler_alias):
    Base.metadata.clear()
    storage = {1: {"id": 1, "value": "a"}}
    calls = []

    async def fake_update(model, ident, data, db=None):
        calls.append("core")
        storage[ident].update(data)
        return storage[ident]

    monkeypatch.setattr(core, "update", fake_update)

    deco = {"target": "update"}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Gizmo(Base):
        __tablename__ = f"gizmos_update_{handler_alias}"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(**deco)
        def update(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "payload": {"value": "b"}, "db": object()}
    ctx_before = ctx.copy()
    handler = getattr(Gizmo.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"id": 1, "value": "b"}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1, "value": "b"}}
    assert calls == ["core"]


@pytest.mark.asyncio
async def test_op_ctx_alias_update_overrides_core(monkeypatch):
    Base.metadata.clear()
    storage = {1: {"id": 1, "value": "a"}}
    calls = []

    async def fake_update(model, ident, data, db=None):
        calls.append("core")
        storage[ident].update(data)
        return storage[ident]

    monkeypatch.setattr(core, "update", fake_update)

    class Device(Base):
        __tablename__ = "devices_custom_update"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(alias="update")
        def custom(cls, ctx):
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "payload": {"value": "b"}, "db": object()}
    ctx_before = ctx.copy()
    result = await Device.handlers.update.raw(ctx)
    assert result == {"id": 99}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1, "value": "a"}}
    assert calls == ["custom"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "alias_kw, handler_alias",
    [(None, "replace"), ("replace", "replace"), ("swap", "swap")],
)
async def test_op_ctx_target_replace_core_executes(
    monkeypatch, alias_kw, handler_alias
):
    Base.metadata.clear()
    storage = {1: {"id": 1, "value": "a"}}
    calls = []

    async def fake_replace(model, ident, data, db=None):
        calls.append("core")
        storage[ident] = {"id": ident, **data}
        return storage[ident]

    monkeypatch.setattr(core, "replace", fake_replace)

    deco = {"target": "replace"}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Thing(Base):
        __tablename__ = f"things_replace_{handler_alias}"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(**deco)
        def replace(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "payload": {"value": "c"}, "db": object()}
    ctx_before = ctx.copy()
    handler = getattr(Thing.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"id": 1, "value": "c"}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1, "value": "c"}}
    assert calls == ["core"]


@pytest.mark.asyncio
async def test_op_ctx_alias_replace_overrides_core(monkeypatch):
    Base.metadata.clear()
    storage = {1: {"id": 1, "value": "a"}}
    calls = []

    async def fake_replace(model, ident, data, db=None):
        calls.append("core")
        storage[ident] = {"id": ident, **data}
        return storage[ident]

    monkeypatch.setattr(core, "replace", fake_replace)

    class Part(Base):
        __tablename__ = "parts_custom_replace"
        id = Column(Integer, primary_key=True)
        value = Column(String)

        @op_ctx(alias="replace")
        def custom(cls, ctx):
            calls.append("custom")
            ctx["touched"] = True
            return {"id": 99}

    ctx = {"path_params": {"id": 1}, "payload": {"value": "c"}, "db": object()}
    ctx_before = ctx.copy()
    result = await Part.handlers.replace.raw(ctx)
    assert result == {"id": 99}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1, "value": "a"}}
    assert calls == ["custom"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "alias_kw, handler_alias",
    [(None, "delete"), ("delete", "delete"), ("remove", "remove")],
)
async def test_op_ctx_target_delete_core_executes(monkeypatch, alias_kw, handler_alias):
    Base.metadata.clear()
    storage = {1: {"id": 1}}
    calls = []

    async def fake_delete(model, ident, db=None):
        calls.append("core")
        storage.pop(ident, None)
        return {"deleted": 1}

    monkeypatch.setattr(core, "delete", fake_delete)

    deco = {"target": "delete"}
    if alias_kw is not None:
        deco["alias"] = alias_kw

    class Piece(Base):
        __tablename__ = f"pieces_delete_{handler_alias}"
        id = Column(Integer, primary_key=True)

        @op_ctx(**deco)
        def delete(cls, ctx):  # pragma: no cover - never executed
            calls.append("custom")
            ctx["touched"] = True
            return {"deleted": 0}

    ctx = {"path_params": {"id": 1}, "db": object()}
    ctx_before = ctx.copy()
    handler = getattr(Piece.handlers, handler_alias).raw
    result = await handler(ctx)
    assert result == {"deleted": 1}
    assert ctx == ctx_before
    assert storage == {}
    assert calls == ["core"]


@pytest.mark.asyncio
async def test_op_ctx_alias_delete_overrides_core(monkeypatch):
    Base.metadata.clear()
    storage = {1: {"id": 1}}
    calls = []

    async def fake_delete(model, ident, db=None):
        calls.append("core")
        storage.pop(ident, None)
        return {"deleted": 1}

    monkeypatch.setattr(core, "delete", fake_delete)

    class Chip(Base):
        __tablename__ = "chips_custom_delete"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias="delete")
        def custom(cls, ctx):
            calls.append("custom")
            ctx["touched"] = True
            return {"deleted": 0}

    ctx = {"path_params": {"id": 1}, "db": object()}
    ctx_before = ctx.copy()
    result = await Chip.handlers.delete.raw(ctx)
    assert result == {"deleted": 0}
    assert ctx == ctx_before
    assert storage == {1: {"id": 1}}
    assert calls == ["custom"]
