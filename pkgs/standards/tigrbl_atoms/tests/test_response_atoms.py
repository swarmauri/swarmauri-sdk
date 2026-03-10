from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.response import REGISTRY
from tigrbl_atoms.atoms.response import (
    error_to_transport,
    headers_from_payload,
    negotiate,
    render,
    template,
)
from tigrbl_atoms.atoms.response.renderer import ResponseHints
from tigrbl_atoms.types import Atom, EncodedCtx


def test_response_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("response", "template"),
        ("response", "negotiate"),
        ("response", "headers_from_payload"),
        ("response", "render"),
        ("response", "error_to_transport"),
    }


def test_response_registry_binds_expected_anchors_and_instances() -> None:
    assert REGISTRY[("response", "template")] == (template.ANCHOR, template.INSTANCE)
    assert REGISTRY[("response", "negotiate")] == (negotiate.ANCHOR, negotiate.INSTANCE)
    assert REGISTRY[("response", "headers_from_payload")] == (
        headers_from_payload.ANCHOR,
        headers_from_payload.INSTANCE,
    )
    assert REGISTRY[("response", "render")] == (render.ANCHOR, render.INSTANCE)
    assert REGISTRY[("response", "error_to_transport")] == (
        error_to_transport.ANCHOR,
        error_to_transport.INSTANCE,
    )


def test_response_instances_and_impls_use_atom_contract() -> None:
    modules = (template, negotiate, headers_from_payload, render, error_to_transport)
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_negotiate_sets_media_type_from_accept_header() -> None:
    ctx = SimpleNamespace(
        status_code=200,
        request=SimpleNamespace(headers={"accept": "text/plain"}),
        response=SimpleNamespace(
            result={"ok": True}, hints=None, default_media="application/json"
        ),
    )

    negotiate._run(None, ctx)

    assert ctx.response.hints.media_type == "text/plain"


def test_headers_from_payload_maps_payload_field_to_header() -> None:
    io = SimpleNamespace(header_out="x-request-id", out_verbs=("create",))
    spec = SimpleNamespace(io=io)
    ctx = SimpleNamespace(
        status_code=200,
        op="create",
        response=SimpleNamespace(result={"request_id": "abc"}, hints=None),
        specs={"request_id": spec},
    )

    headers_from_payload._run(None, ctx)

    assert ctx.response.hints.headers["x-request-id"] == "abc"


def test_render_builds_transport_response_for_non_jsonrpc() -> None:
    ctx = SimpleNamespace(
        status_code=201,
        request=SimpleNamespace(headers={}),
        response=SimpleNamespace(
            result={"ok": True},
            hints=ResponseHints(status_code=201),
            default_media="application/json",
            envelope_default=False,
        ),
        temp={},
    )

    response_obj = render._run(None, ctx)

    assert response_obj is not None
    assert "transport_response" in ctx.temp["egress"]
    assert ctx.temp["egress"]["transport_response"]["status_code"] == 201


def test_error_to_transport_writes_standard_error_payload() -> None:
    ctx = SimpleNamespace(error=ValueError("boom"), temp={})

    asyncio.run(error_to_transport._run(None, ctx))

    tr = ctx.temp["egress"]["transport_response"]
    assert tr["status_code"] == 400
    assert tr["headers"]["content-type"] == "application/json"
    assert tr["body"]["detail"] == "<class 'ValueError'>: boom"


def test_template_run_sets_html_result_and_media_type(monkeypatch) -> None:
    async def fake_render_template(**kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["name"] == "page.html"
        assert kwargs["context"] == {"name": "Ada"}
        return "<h1>Ada</h1>"

    monkeypatch.setattr(template, "render_template", fake_render_template)

    ctx = SimpleNamespace(
        status_code=200,
        request=SimpleNamespace(url_for=lambda *_a, **_k: "/"),
        response=SimpleNamespace(
            result={"name": "Ada"},
            template=SimpleNamespace(
                name="page.html",
                search_paths=(),
                package=None,
                auto_reload=False,
                filters=None,
                globals=None,
            ),
            hints=None,
        ),
    )

    asyncio.run(template._run(None, ctx))

    assert ctx.response.result == "<h1>Ada</h1>"
    assert ctx.response.hints.media_type == "text/html"


def test_response_instances_promote_to_encoded_ctx(monkeypatch) -> None:
    monkeypatch.setattr(negotiate, "_run", lambda _obj, _ctx: None)
    monkeypatch.setattr(render, "_run", lambda _obj, _ctx: None)
    monkeypatch.setattr(headers_from_payload, "_run", lambda _obj, _ctx: None)

    ctx = EncodedCtx()

    negotiated = asyncio.run(negotiate.INSTANCE(None, ctx))
    rendered = asyncio.run(render.INSTANCE(None, ctx))
    headed = asyncio.run(headers_from_payload.INSTANCE(None, ctx))

    assert isinstance(negotiated, EncodedCtx)
    assert isinstance(rendered, EncodedCtx)
    assert isinstance(headed, EncodedCtx)
