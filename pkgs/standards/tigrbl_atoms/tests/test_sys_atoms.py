from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.sys import REGISTRY
from tigrbl_atoms.atoms.sys import (
    commit_tx,
    handler_bulk_create,
    handler_bulk_delete,
    handler_bulk_merge,
    handler_bulk_replace,
    handler_bulk_update,
    handler_clear,
    handler_create,
    handler_custom,
    handler_delete,
    handler_list,
    handler_merge,
    handler_noop,
    handler_persistence,
    handler_read,
    handler_replace,
    handler_update,
    start_tx,
)
from tigrbl_atoms.types import Atom, ExecutingCtx, GuardedCtx, OperatedCtx, ResolvedCtx


def test_sys_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("sys", "start_tx"),
        ("sys", "handler_persistence"),
        ("sys", "handler_create"),
        ("sys", "handler_read"),
        ("sys", "handler_update"),
        ("sys", "handler_replace"),
        ("sys", "handler_merge"),
        ("sys", "handler_noop"),
        ("sys", "handler_delete"),
        ("sys", "handler_list"),
        ("sys", "handler_clear"),
        ("sys", "handler_bulk_create"),
        ("sys", "handler_bulk_update"),
        ("sys", "handler_bulk_replace"),
        ("sys", "handler_bulk_merge"),
        ("sys", "handler_bulk_delete"),
        ("sys", "commit_tx"),
    }


def test_sys_registry_binds_expected_anchor_and_instance_samples() -> None:
    assert REGISTRY[("sys", "start_tx")] == (start_tx.ANCHOR, start_tx.INSTANCE)
    assert REGISTRY[("sys", "handler_create")] == (
        handler_create.ANCHOR,
        handler_create.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_read")] == (
        handler_read.ANCHOR,
        handler_read.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_update")] == (
        handler_update.ANCHOR,
        handler_update.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_replace")] == (
        handler_replace.ANCHOR,
        handler_replace.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_merge")] == (
        handler_merge.ANCHOR,
        handler_merge.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_delete")] == (
        handler_delete.ANCHOR,
        handler_delete.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_list")] == (
        handler_list.ANCHOR,
        handler_list.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_clear")] == (
        handler_clear.ANCHOR,
        handler_clear.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_bulk_create")] == (
        handler_bulk_create.ANCHOR,
        handler_bulk_create.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_bulk_update")] == (
        handler_bulk_update.ANCHOR,
        handler_bulk_update.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_bulk_replace")] == (
        handler_bulk_replace.ANCHOR,
        handler_bulk_replace.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_bulk_merge")] == (
        handler_bulk_merge.ANCHOR,
        handler_bulk_merge.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_bulk_delete")] == (
        handler_bulk_delete.ANCHOR,
        handler_bulk_delete.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_persistence")] == (
        handler_persistence.ANCHOR,
        handler_persistence.INSTANCE,
    )
    assert REGISTRY[("sys", "handler_noop")] == (
        handler_noop.ANCHOR,
        handler_noop.INSTANCE,
    )
    assert REGISTRY[("sys", "commit_tx")] == (commit_tx.ANCHOR, commit_tx.INSTANCE)


def test_sys_instances_and_impls_use_atom_contract() -> None:
    modules = (
        start_tx,
        commit_tx,
        handler_persistence,
        handler_create,
        handler_read,
        handler_update,
        handler_replace,
        handler_merge,
        handler_delete,
        handler_list,
        handler_clear,
        handler_bulk_create,
        handler_bulk_update,
        handler_bulk_replace,
        handler_bulk_merge,
        handler_bulk_delete,
        handler_noop,
    )
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_start_tx_marks_open_and_commit_tx_commits_and_releases() -> None:
    calls: list[str] = []

    class DB:
        async def begin(self) -> None:
            calls.append("begin")

        async def commit(self) -> None:
            calls.append("commit")

    temp = {"__sys_db_release__": lambda: calls.append("release")}
    tx_ctx = SimpleNamespace(db=DB(), temp=temp)

    asyncio.run(start_tx._run(None, tx_ctx))
    assert tx_ctx.temp["__sys_tx_open__"] is True

    asyncio.run(commit_tx._run(None, tx_ctx))
    assert calls == ["begin", "commit", "release"]
    assert tx_ctx.temp["__sys_tx_open__"] is False
    assert "__sys_db_release__" not in tx_ctx.temp


def test_handler_noop_sets_default_result_shape() -> None:
    ctx = SimpleNamespace(op="custom_alias")

    asyncio.run(handler_noop._run(None, ctx))

    assert ctx.result == {
        "ok": True,
        "noop": True,
        "alias": "custom_alias",
        "target": "noop",
    }


def test_handler_custom_bind_sets_result_for_sync_and_async() -> None:
    sync_atom = handler_custom.bind(lambda _obj, _ctx: {"kind": "sync"})
    async_atom = handler_custom.bind(
        lambda _obj, _ctx: asyncio.sleep(0, result={"kind": "async"})
    )

    sync_ctx = OperatedCtx()
    async_ctx = OperatedCtx()

    sync_out = asyncio.run(sync_atom(None, sync_ctx))
    async_out = asyncio.run(async_atom(None, async_ctx))

    assert sync_ctx.result == {"kind": "sync"}
    assert async_ctx.result == {"kind": "async"}
    assert isinstance(sync_out, OperatedCtx)
    assert isinstance(async_out, OperatedCtx)


def test_handler_create_delegates_to_core_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Model:
        pass

    async def fake_create(
        model: type, payload: object, db: object
    ) -> dict[str, object]:
        assert model is Model
        assert payload == {"name": "Ada", "age": 3}
        assert db == "db-handle"
        return {"id": 1}

    monkeypatch.setattr(handler_create._core, "create", fake_create)

    ctx = SimpleNamespace(
        payload={"name": "Ada"},
        temp={"assembled_values": {"age": 3}},
        db="db-handle",
    )

    asyncio.run(handler_create._run(Model, ctx))

    assert ctx.result == {"id": 1}


@pytest.mark.parametrize(
    ("atom", "core_name", "payload", "expected"),
    (
        (handler_read, "read", {"id": 7}, {"id": 7}),
        (handler_update, "update", {"name": "Ada"}, {"updated": True}),
        (handler_replace, "replace", {"name": "Grace"}, {"replaced": True}),
        (handler_merge, "merge", {"name": "Linus"}, {"merged": True}),
        (handler_delete, "delete", {"id": 7}, {"deleted": True}),
    ),
)
def test_handlers_delegate_to_core_with_ident_and_db(
    monkeypatch: pytest.MonkeyPatch,
    atom: Atom,
    core_name: str,
    payload: dict[str, object],
    expected: dict[str, object],
) -> None:
    class Model:
        pass

    async def fake_call(*args: object, **kwargs: object) -> dict[str, object]:
        assert args[0] is Model
        assert args[1] == 7
        if core_name != "read":
            assert args[2] == payload
        assert kwargs == {"db": "db-handle"}
        return expected

    monkeypatch.setattr(atom._core, core_name, fake_call)

    ctx = SimpleNamespace(payload=payload, path_params={"id": 7}, db="db-handle")
    asyncio.run(atom._run(Model, ctx))

    assert ctx.result == expected


def test_handler_clear_delegates_to_core_clear_with_empty_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Model:
        pass

    async def fake_clear(model: type, filters: object, db: object) -> dict[str, object]:
        assert model is Model
        assert filters == {}
        assert db == "db-handle"
        return {"cleared": True}

    monkeypatch.setattr(handler_clear._core, "clear", fake_clear)

    ctx = SimpleNamespace(payload={"ignored": True}, db="db-handle")
    asyncio.run(handler_clear._run(Model, ctx))

    assert ctx.result == {"cleared": True}


def test_handler_bulk_create_requires_list_payload() -> None:
    class Model:
        pass

    with pytest.raises(TypeError, match="bulk_create expects a list payload"):
        asyncio.run(handler_bulk_create._run(Model, SimpleNamespace(payload={"x": 1})))


@pytest.mark.parametrize(
    ("atom", "msg"),
    (
        (handler_bulk_update, "bulk_update expects a list payload"),
        (handler_bulk_replace, "bulk_replace expects a list payload"),
        (handler_bulk_merge, "bulk_merge expects a list payload"),
    ),
)
def test_bulk_handlers_require_list_payload(atom: Atom, msg: str) -> None:
    class Model:
        pass

    with pytest.raises(TypeError, match=msg):
        asyncio.run(atom._run(Model, SimpleNamespace(payload={"x": 1})))


def test_handler_bulk_delete_uses_ids_from_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Model:
        pass

    async def fake_bulk_delete(
        model: type, ids: object, db: object
    ) -> dict[str, object]:
        assert model is Model
        assert ids == [1, 3, 5]
        assert db == "db-handle"
        return {"deleted": 3}

    monkeypatch.setattr(handler_bulk_delete._core, "bulk_delete", fake_bulk_delete)

    ctx = SimpleNamespace(payload={"ids": [1, 3, 5]}, db="db-handle")

    asyncio.run(handler_bulk_delete._run(Model, ctx))

    assert ctx.result == {"deleted": 3}


@pytest.mark.parametrize(
    ("atom", "core_name", "expected"),
    (
        (handler_bulk_create, "bulk_create", {"created": 2}),
        (handler_bulk_update, "bulk_update", {"updated": 2}),
        (handler_bulk_replace, "bulk_replace", {"replaced": 2}),
        (handler_bulk_merge, "bulk_merge", {"merged": 2}),
    ),
)
def test_bulk_handlers_delegate_list_payload_to_core(
    monkeypatch: pytest.MonkeyPatch,
    atom: Atom,
    core_name: str,
    expected: dict[str, object],
) -> None:
    class Model:
        pass

    payload = [{"id": 1}, {"id": 2}]

    async def fake_bulk(
        model: type, incoming_payload: object, db: object
    ) -> dict[str, object]:
        assert model is Model
        assert incoming_payload == payload
        assert db == "db-handle"
        return expected

    monkeypatch.setattr(atom._core, core_name, fake_bulk)

    ctx = SimpleNamespace(payload=payload, db="db-handle")
    asyncio.run(atom._run(Model, ctx))

    assert ctx.result == expected


def test_handler_list_passes_filters_and_pagination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Model:
        pass

    async def fake_list(  # type: ignore[no-untyped-def]
        model, *, filters=None, db=None, request=None, skip=None, limit=None
    ):
        assert model is Model
        assert filters == {"status": "active"}
        assert db == "db-handle"
        assert request == "request-handle"
        assert skip == 2
        assert limit == 5
        return [{"id": 1}]

    monkeypatch.setattr(handler_list._core, "list", fake_list)

    ctx = SimpleNamespace(
        payload={"status": "active", "skip": 2, "limit": 5},
        db="db-handle",
        request="request-handle",
    )

    asyncio.run(handler_list._run(Model, ctx))

    assert ctx.result == [{"id": 1}]


def test_sys_instances_promote_expected_ctx_types() -> None:
    guarded = GuardedCtx()
    resolved = ResolvedCtx()
    resolved_with_result_slot = OperatedCtx()
    operated = OperatedCtx()

    started = asyncio.run(start_tx.INSTANCE(None, guarded))
    persisted = asyncio.run(handler_persistence.INSTANCE(None, resolved))
    nooped = asyncio.run(handler_noop.INSTANCE(None, resolved_with_result_slot))
    committed = asyncio.run(commit_tx.INSTANCE(None, operated))

    assert isinstance(started, ExecutingCtx)
    assert isinstance(persisted, OperatedCtx)
    assert isinstance(nooped, OperatedCtx)
    assert isinstance(committed, OperatedCtx)
