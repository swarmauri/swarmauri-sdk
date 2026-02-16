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
    assert openrpc_doc["servers"] == [{"name": app.title, "url": "/jsonrpc"}]
    assert "swagger-ui" in swagger_html
    assert "tigrbl-lens" in lens_html
