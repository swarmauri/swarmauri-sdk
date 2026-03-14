from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.ingress import REGISTRY
from tigrbl_atoms.atoms.ingress import ctx_init, input_prepare, transport_extract
from tigrbl_atoms.types import Atom


def test_ingress_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("ingress", "ctx_init"),
        ("ingress", "transport_extract"),
        ("ingress", "input_prepare"),
    }


def test_ingress_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("ingress", "ctx_init")] == (ctx_init.ANCHOR, ctx_init.INSTANCE)
    assert REGISTRY[("ingress", "transport_extract")] == (
        transport_extract.ANCHOR,
        transport_extract.INSTANCE,
    )
    assert REGISTRY[("ingress", "input_prepare")] == (
        input_prepare.ANCHOR,
        input_prepare.INSTANCE,
    )


def test_ingress_instances_and_impls_use_atom_contract() -> None:
    for module in (ctx_init, transport_extract, input_prepare):
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_ctx_init_sets_ingress_flags() -> None:
    ctx = SimpleNamespace()
    ctx_init._run(None, ctx)
    assert ctx.temp["ingress"]["ctx_initialized"] is True
    assert isinstance(ctx.temp["ingress"]["started_at"], float)


def test_transport_extract_and_input_prepare_fill_ingress_fields() -> None:
    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b'{"a":1}', "more_body": False}

    ctx = SimpleNamespace(
        raw=SimpleNamespace(
            scope={
                "type": "http",
                "method": "post",
                "path": "/v1/widgets",
                "scheme": "https",
                "headers": [(b"content-type", b"application/json"), (b"x-a", b"1")],
                "query_string": b"x=1&x=2",
            },
            receive=_receive,
        ),
        app=SimpleNamespace(),
    )

    asyncio.run(transport_extract._run(None, ctx))
    input_prepare._run(None, ctx)

    assert ctx.method == "POST"
    assert ctx.path == "/v1/widgets"
    assert ctx.query["x"] == ["1", "2"]
    assert ctx.headers["content-type"] == "application/json"
    assert ctx.body == b'{"a":1}'
    assert ctx.temp["ingress"]["body_json"] == {"a": 1}
