from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.ingress import REGISTRY
from tigrbl_atoms.atoms.ingress import (
    attach_compiled,
    body_peek,
    body_read,
    ctx_init,
    headers_parse,
    method_extract,
    metrics_start,
    path_extract,
    query_parse,
    raw_from_scope,
    request_body_apply,
    request_from_scope,
)
from tigrbl_atoms.types import Atom


def test_ingress_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("ingress", "ctx_init"),
        ("ingress", "attach_compiled"),
        ("ingress", "metrics_start"),
        ("ingress", "raw_from_scope"),
        ("ingress", "method_extract"),
        ("ingress", "path_extract"),
        ("ingress", "request_from_scope"),
        ("ingress", "headers_parse"),
        ("ingress", "query_parse"),
        ("ingress", "body_read"),
        ("ingress", "request_body_apply"),
        ("ingress", "body_peek"),
    }


def test_ingress_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("ingress", "ctx_init")] == (ctx_init.ANCHOR, ctx_init.INSTANCE)
    assert REGISTRY[("ingress", "attach_compiled")] == (
        attach_compiled.ANCHOR,
        attach_compiled.INSTANCE,
    )
    assert REGISTRY[("ingress", "metrics_start")] == (
        metrics_start.ANCHOR,
        metrics_start.INSTANCE,
    )
    assert REGISTRY[("ingress", "raw_from_scope")] == (
        raw_from_scope.ANCHOR,
        raw_from_scope.INSTANCE,
    )
    assert REGISTRY[("ingress", "method_extract")] == (
        method_extract.ANCHOR,
        method_extract.INSTANCE,
    )
    assert REGISTRY[("ingress", "path_extract")] == (
        path_extract.ANCHOR,
        path_extract.INSTANCE,
    )
    assert REGISTRY[("ingress", "request_from_scope")] == (
        request_from_scope.ANCHOR,
        request_from_scope.INSTANCE,
    )
    assert REGISTRY[("ingress", "headers_parse")] == (
        headers_parse.ANCHOR,
        headers_parse.INSTANCE,
    )
    assert REGISTRY[("ingress", "query_parse")] == (
        query_parse.ANCHOR,
        query_parse.INSTANCE,
    )
    assert REGISTRY[("ingress", "body_read")] == (body_read.ANCHOR, body_read.INSTANCE)
    assert REGISTRY[("ingress", "request_body_apply")] == (
        request_body_apply.ANCHOR,
        request_body_apply.INSTANCE,
    )
    assert REGISTRY[("ingress", "body_peek")] == (body_peek.ANCHOR, body_peek.INSTANCE)


def test_ingress_instances_and_impls_use_atom_contract() -> None:
    modules = (
        ctx_init,
        attach_compiled,
        metrics_start,
        raw_from_scope,
        method_extract,
        path_extract,
        request_from_scope,
        headers_parse,
        query_parse,
        body_read,
        request_body_apply,
        body_peek,
    )
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_ctx_init_sets_ingress_flags() -> None:
    ctx = SimpleNamespace()
    ctx_init._run(None, ctx)
    assert ctx.temp["ingress"]["ctx_initialized"] is True
    assert isinstance(ctx.temp["ingress"]["started_at"], float)


def test_attach_compiled_reads_kernel_plan_compiled() -> None:
    compiled = object()
    ctx = SimpleNamespace(kernel_plan=SimpleNamespace(compiled=compiled))
    attach_compiled._run(None, ctx)
    assert ctx.temp["ingress"]["compiled"] is compiled


def test_metrics_start_sets_timestamps() -> None:
    ctx = SimpleNamespace()
    metrics_start._run(None, ctx)
    assert isinstance(ctx.temp["metrics"]["ingress_started_at"], float)
    assert isinstance(ctx.temp["metrics"]["ingress_started_ns"], int)


def test_raw_from_scope_builds_http_route_envelope() -> None:
    ctx = SimpleNamespace(
        app=SimpleNamespace(jsonrpc_prefix="/rpc"),
        body=b'{"jsonrpc":"2.0","id":1,"method":"ping"}',
        raw=SimpleNamespace(
            scope={
                "type": "http",
                "scheme": "https",
                "method": "POST",
                "path": "/rpc",
                "headers": [(b"content-type", b"application/json")],
                "query_string": b"a=1&a=2",
            }
        ),
    )

    raw_from_scope._run(None, ctx)

    assert ctx.gw_raw.transport == "http"
    assert ctx.gw_raw.kind == "maybe-jsonrpc"
    assert ctx.temp["ingress"]["raw_path"] == "/rpc"
    assert ctx.temp["ingress"]["raw_query"]["a"] == ["1", "2"]


def test_extract_parse_and_body_atoms_fill_ingress_fields() -> None:
    ctx = SimpleNamespace(
        raw=SimpleNamespace(
            scope={
                "method": "post",
                "path": "/v1/widgets",
                "headers": [(b"x-a", b"1"), (b"x-a", b"2")],
                "query_string": b"x=1&x=2",
            }
        ),
        body="hello",
    )

    method_extract._run(None, ctx)
    path_extract._run(None, ctx)
    headers_parse._run(None, ctx)
    query_parse._run(None, ctx)
    asyncio.run(body_read._run(None, ctx))
    body_peek._run(None, ctx)

    assert ctx.method == "POST"
    assert ctx.path == "/v1/widgets"
    assert ctx.headers["x-a"] == ["1", "2"]
    assert ctx.query["x"] == ["1", "2"]
    assert ctx.body == b"hello"
    assert ctx.temp["ingress"]["body_peek"] == b"hello"


def test_request_body_apply_sets_bytes_on_request() -> None:
    req = SimpleNamespace(body=None)
    ctx = SimpleNamespace(request=req, body="payload")

    request_body_apply._run(None, ctx)

    assert req.body == b"payload"
