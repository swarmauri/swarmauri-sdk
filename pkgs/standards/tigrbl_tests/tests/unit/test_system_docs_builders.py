import pytest

from tigrbl import TigrblApp
from tigrbl.system import build_lens, build_openapi, build_openrpc_spec, build_swagger
from tigrbl.types import Request


@pytest.mark.unit
def test_system_build_helpers_return_documents() -> None:
    app = TigrblApp()
    request = Request(
        method="GET", path="/docs", headers={}, query={}, path_params={}, body=b""
    )

    openapi_doc = build_openapi(app)
    openrpc_doc = build_openrpc_spec(app)
    swagger_html = build_swagger(app, request)
    lens_html = build_lens(app, request, spec_path="/openrpc.json")

    assert openapi_doc["openapi"].startswith("3.")
    assert openrpc_doc["openrpc"] == "1.2.6"
    assert openrpc_doc["servers"] == [{"name": app.title, "url": "/rpc"}]
    assert "swagger-ui" in swagger_html
    assert "tigrbl-lens" in lens_html


@pytest.mark.unit
def test_openrpc_builder_uses_request_origin_and_jsonrpc_prefix() -> None:
    app = TigrblApp(jsonrpc_prefix="/gateway/rpc")
    request = Request(
        method="GET",
        path="/openrpc.json",
        headers={"host": "router.example.com", "x-forwarded-proto": "https"},
        query={},
        path_params={},
        body=b"",
    )

    openrpc_doc = build_openrpc_spec(app, request=request)

    assert openrpc_doc["servers"] == [
        {"name": app.title, "url": "https://router.example.com/gateway/rpc"}
    ]


@pytest.mark.unit
def test_openrpc_builder_normalizes_forwarded_host_header_values() -> None:
    app = TigrblApp(jsonrpc_prefix="/gateway/rpc")
    request = Request(
        method="GET",
        path="/openrpc.json",
        headers={
            "x-forwarded-host": "router.example.com,edge.proxy.internal",
            "x-forwarded-proto": "https, http",
        },
        query={},
        path_params={},
        body=b"",
    )

    openrpc_doc = build_openrpc_spec(app, request=request)

    assert openrpc_doc["servers"] == [
        {"name": app.title, "url": "https://router.example.com/gateway/rpc"}
    ]


@pytest.mark.unit
def test_openrpc_builder_prefers_request_scheme_without_forwarded_proto() -> None:
    app = TigrblApp(jsonrpc_prefix="/gateway/rpc")
    request = Request(
        method="GET",
        path="/openrpc.json",
        headers={"x-forwarded-host": "router.example.com"},
        query={},
        path_params={},
        body=b"",
        scope={"scheme": "https"},
    )

    openrpc_doc = build_openrpc_spec(app, request=request)

    assert openrpc_doc["servers"] == [
        {"name": app.title, "url": "https://router.example.com/gateway/rpc"}
    ]


@pytest.mark.unit
def test_openrpc_builder_prefers_forwarded_proto_over_request_scheme() -> None:
    app = TigrblApp(jsonrpc_prefix="/gateway/rpc")
    request = Request(
        method="GET",
        path="/openrpc.json",
        headers={"host": "router.example.com", "x-forwarded-proto": "https"},
        query={},
        path_params={},
        body=b"",
        scope={"scheme": "http"},
    )

    openrpc_doc = build_openrpc_spec(app, request=request)

    assert openrpc_doc["servers"] == [
        {"name": app.title, "url": "https://router.example.com/gateway/rpc"}
    ]


@pytest.mark.unit
def test_openrpc_builder_keeps_relative_server_url_without_forwarding_headers() -> None:
    app = TigrblApp(jsonrpc_prefix="/gateway/rpc")
    request = Request(
        method="GET",
        path="/openrpc.json",
        headers={"host": "router.example.com"},
        query={},
        path_params={},
        body=b"",
    )

    openrpc_doc = build_openrpc_spec(app, request=request)

    assert openrpc_doc["servers"] == [{"name": app.title, "url": "/gateway/rpc"}]
