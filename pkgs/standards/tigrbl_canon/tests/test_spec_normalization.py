from __future__ import annotations

from tigrbl_base._base import AppBase

from tigrbl_canon.mapping.spec_normalization import merge_seq_attr, normalize_app_spec


class _Base:
    tags = ("base", "shared")


class _Middle(_Base):
    tags = ["middle", "shared"]


class _Leaf(_Middle):
    tags = ("leaf", "shared")


class _WithUnhashableBase:
    attrs = [{"k": "v"}]


class _WithUnhashableChild(_WithUnhashableBase):
    attrs = [{"k": "v"}, {"k": "w"}]


def test_merge_seq_attr_merges_mro_and_dedupes_by_default() -> None:
    assert merge_seq_attr(_Leaf, "tags") == ("leaf", "shared", "middle", "base")


def test_merge_seq_attr_reverse_keeps_oldest_first() -> None:
    assert merge_seq_attr(_Leaf, "tags", reverse=True) == (
        "base",
        "shared",
        "middle",
        "leaf",
    )


def test_merge_seq_attr_dedupes_unhashable_values_by_equality() -> None:
    merged = merge_seq_attr(_WithUnhashableChild, "attrs")

    assert merged == ({"k": "v"}, {"k": "w"})


def test_normalize_app_spec_coerces_defaults_and_sequences() -> None:
    spec = AppBase(
        title=None,
        version=None,
        routers=["router_a"],
        ops="op_a",
        hooks=None,
        schemas={"schema": "value"},
        deps=None,
        security_deps="auth",
        middlewares=("mw",),
        jsonrpc_prefix=None,
        system_prefix=None,
    )

    normalized = normalize_app_spec(spec)

    assert normalized.title == "Tigrbl"
    assert normalized.version == "0.1.0"
    assert normalized.routers == ("router_a",)
    assert normalized.ops == ("op_a",)
    assert normalized.schemas == ({"schema": "value"},)
    assert normalized.hooks == ()
    assert normalized.deps == ()
    assert normalized.security_deps == ("auth",)
    assert normalized.middlewares == ("mw",)
    assert normalized.jsonrpc_prefix == "/rpc"
    assert normalized.system_prefix == "/system"
