from __future__ import annotations

import asyncio
import datetime as dt
import decimal as dc
import uuid
from types import SimpleNamespace

import pytest
from tigrbl_typing.status.exceptions import HTTPException

from tigrbl_atoms.atoms.wire import REGISTRY
from tigrbl_atoms.atoms.wire import build_in, build_out, dump, validate_in
from tigrbl_atoms.types import Atom, EncodedCtx, ExecutingCtx, OperatedCtx


def test_wire_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("wire", "build_in"),
        ("wire", "validate_in"),
        ("wire", "build_out"),
        ("wire", "dump"),
    }


def test_wire_registry_binds_expected_anchors_and_instances() -> None:
    assert REGISTRY[("wire", "build_in")] == (build_in.ANCHOR, build_in.INSTANCE)
    assert REGISTRY[("wire", "validate_in")] == (
        validate_in.ANCHOR,
        validate_in.INSTANCE,
    )
    assert REGISTRY[("wire", "build_out")] == (build_out.ANCHOR, build_out.INSTANCE)
    assert REGISTRY[("wire", "dump")] == (dump.ANCHOR, dump.INSTANCE)


def test_wire_instances_and_impls_use_atom_contract() -> None:
    modules = (build_in, validate_in, build_out, dump)
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_build_in_maps_aliases_and_tracks_unknown_keys() -> None:
    ctx = SimpleNamespace(
        payload={"display_name": "Ada", "extra": 9},
        temp={
            "schema_in": {
                "fields": ("name",),
                "by_field": {"name": {"alias_in": "display_name"}},
                "required": ("name",),
            }
        },
    )

    build_in._run(None, ctx)

    assert ctx.temp["in_values"] == {"name": "Ada"}
    assert ctx.temp["in_present"] == ("name",)
    assert ctx.temp["in_unknown"] == ("extra",)
    assert ctx.temp["in_unknown_samples"] == {"extra": 9}


def test_build_in_rejects_disallowed_wrapper_keys() -> None:
    ctx = SimpleNamespace(
        payload={"data": {"name": "Ada"}},
        temp={
            "route": {"rpc_envelope": {"jsonrpc": "2.0"}},
            "schema_in": {
                "fields": ("name",),
                "by_field": {"name": {}},
                "required": (),
            },
        },
    )

    with pytest.raises(HTTPException) as exc:
        build_in._run(None, ctx)

    assert exc.value.status_code == 422
    assert "disallowed_keys" in exc.value.detail
    assert exc.value.detail["disallowed_keys"] == ["data"]


def test_validate_in_coerces_values_and_runs_custom_validator() -> None:
    ctx = SimpleNamespace(
        temp={
            "schema_in": {
                "fields": ("count", "name"),
                "required": ("count",),
                "by_field": {
                    "count": {"py_type": int, "coerce": True, "nullable": False},
                    "name": {
                        "py_type": str,
                        "validator": lambda value, _ctx: value.strip().title(),
                    },
                },
            },
            "in_values": {"count": "7", "name": "  ada  "},
        }
    )

    validate_in._run(None, ctx)

    assert ctx.temp["in_values"] == {"count": 7, "name": "Ada"}
    assert ctx.temp["in_coerced"] == ("count",)
    assert ctx.temp["in_invalid"] is False


def test_validate_in_rejects_required_and_unknown_fields_when_configured() -> None:
    ctx = SimpleNamespace(
        cfg=SimpleNamespace(reject_unknown_fields=True),
        temp={
            "schema_in": {
                "fields": ("name",),
                "required": ("name",),
                "by_field": {"name": {"nullable": False}},
            },
            "in_values": {},
            "in_unknown": ("mystery",),
        },
    )

    with pytest.raises(HTTPException) as exc:
        validate_in._run(None, ctx)

    assert exc.value.status_code == 422
    assert ctx.temp["in_invalid"] is True
    codes = {item["code"] for item in ctx.temp["in_errors"]}
    assert "required" in codes
    assert "unknown_field" in codes


def test_build_out_reads_values_and_produces_virtuals() -> None:
    obj = SimpleNamespace(name="Ada")
    ctx = SimpleNamespace(
        temp={
            "schema_out": {
                "fields": ("name", "greeting"),
                "by_field": {
                    "name": {"virtual": False},
                    "greeting": {"virtual": True},
                },
                "expose": ("name", "greeting"),
            }
        },
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(
                fields=("name", "greeting"),
                by_field={
                    "name": {"virtual": False},
                    "greeting": {"virtual": True},
                },
                expose=("name", "greeting"),
            ),
            virtual_producers={"greeting": lambda _obj, _ctx: "Hello"},
        ),
    )

    build_out._run(obj, ctx)

    assert ctx.temp["out_values"] == {"name": "Ada", "greeting": "Hello"}
    assert ctx.temp["out_virtual_produced"] == ("greeting",)


def test_dump_maps_aliases_omits_nulls_and_merges_extras() -> None:
    token = uuid.UUID("12345678-1234-5678-1234-567812345678")
    ctx = SimpleNamespace(
        cfg=SimpleNamespace(exclude_none=True),
        temp={
            "schema_out": {"aliases": {"created_at": "createdAt"}},
            "out_values": {
                "created_at": dt.date(2026, 3, 10),
                "price": dc.Decimal("12.34"),
                "optional": None,
                "token": token,
            },
            "response_extras": {"request_id": "abc-1"},
        },
    )

    dump._run(None, ctx)

    assert ctx.temp["response_payload"] == {
        "createdAt": "2026-03-10",
        "price": "12.34",
        "token": str(token),
        "request_id": "abc-1",
    }


def test_wire_instances_promote_expected_ctx_types() -> None:
    exec_ctx = ExecutingCtx(
        temp={"schema_in": {"fields": (), "by_field": {}, "required": ()}},
    )
    op_ctx = OperatedCtx(
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(fields=(), by_field={}, expose=()),
            virtual_producers={},
        )
    )
    enc_ctx = EncodedCtx(temp={"schema_out": {"aliases": {}}, "out_values": {"x": 1}})

    built = asyncio.run(build_in.INSTANCE(None, exec_ctx))
    validated = asyncio.run(validate_in.INSTANCE(None, exec_ctx))
    out = asyncio.run(build_out.INSTANCE(None, op_ctx))
    dumped = asyncio.run(dump.INSTANCE(None, enc_ctx))

    assert isinstance(built, ExecutingCtx)
    assert isinstance(validated, ExecutingCtx)
    assert isinstance(out, EncodedCtx)
    assert isinstance(dumped, EncodedCtx)
