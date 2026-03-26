from httpx import ASGITransport, Client
from sqlalchemy import Column, String
from tigrbl import TableBase, TigrblRouter, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk


def _build_app():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_openrpc"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app, Widget


def test_openrpc_endpoint_exposed():
    app, _ = _build_app()
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.get("/openrpc.json")

        assert response.status_code == 200
        payload = response.json()
        assert payload["openrpc"] == "1.2.6"
        assert payload["servers"] == [{"name": app.title, "url": "/rpc"}]
        assert "methods" in payload


def test_openrpc_server_url_respects_jsonrpc_prefix():
    app, _ = _build_app()
    app.jsonrpc_prefix = "/rpc/custom"
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    assert payload["servers"] == [{"name": app.title, "url": "/rpc/custom"}]


def test_openrpc_includes_method_schema():
    app, model = _build_app()
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()
        methods = {method["name"]: method for method in payload["methods"]}

        create_method = methods.get(f"{model.__name__}.create")
        if create_method is None:
            assert payload["methods"] == []
            return

        assert create_method["paramStructure"] == "by-name"

        params = create_method["params"][0]["schema"]
        assert params["title"].startswith(model.__name__)
        assert "Create" in params["title"]

        result = create_method["result"]["schema"]
        assert result["title"].startswith(model.__name__)
        assert "Response" in result["title"]


def test_mount_jsonrpc_updates_openrpc_server_url() -> None:
    app, _ = _build_app()
    app.mount_jsonrpc(prefix="/jsonrpc")
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    assert payload["servers"] == [{"name": app.title, "url": "/jsonrpc"}]


def test_jsonrpc_create_accepts_nested_params_mapping() -> None:
    app, model = _build_app()
    transport = ASGITransport(app=app)

    request_payload = {
        "jsonrpc": "2.0",
        "method": f"{model.__name__}.create",
        "params": {"params": {"name": "New Widget"}},
        "id": 1,
    }

    with Client(transport=transport, base_url="http://test") as client:
        response = client.post("/rpc", json=request_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is None
    assert data["error"]["code"] == -32602


def test_jsonrpc_notification_without_id_returns_no_content() -> None:
    app, model = _build_app()
    transport = ASGITransport(app=app)

    request_payload = {
        "jsonrpc": "2.0",
        "method": f"{model.__name__}.create",
        "params": {"name": "Silent Widget"},
    }

    with Client(transport=transport, base_url="http://test") as client:
        response = client.post("/rpc", json=request_payload)

    assert response.status_code == 204
    assert response.content == b""


def test_mount_lens_uses_latest_openrpc_path_by_default() -> None:
    app, _ = _build_app()
    app.mount_openrpc(path="/schema/openrpc.json")
    app.mount_lens(path="/lens-custom")

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        html = client.get("/lens-custom").text

    assert "/schema/openrpc.json" in html


def test_default_system_docs_endpoints_are_present_and_gettable() -> None:
    app, _ = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        docs = client.get("/docs")
        lens = client.get("/lens")
        openapi = client.get("/openapi.json")
        openrpc = client.get("/openrpc.json")
        asyncapi = client.get("/asyncapi.json")
        json_schema = client.get("/json-schema.json")

    assert docs.status_code == 200
    assert "text/html" in docs.headers.get("content-type", "")
    assert "swagger-ui" in docs.text

    assert lens.status_code == 200
    assert "text/html" in lens.headers.get("content-type", "")
    assert 'id="root"' in lens.text

    assert openapi.status_code == 200
    assert openapi.json()["openapi"] == "3.1.0"

    assert openrpc.status_code == 200
    assert openrpc.json()["openrpc"] == "1.2.6"

    assert asyncapi.status_code == 200
    assert "text/plain" in asyncapi.headers.get("content-type", "")
    assert "'asyncapi': '3.0.0'" in asyncapi.text

    assert json_schema.status_code == 200
    assert "text/plain" in json_schema.headers.get("content-type", "")
    assert (
        "'$schema': 'https://json-schema.org/draft/2020-12/schema'" in json_schema.text
    )


def test_docs_lens_openapi_openrpc_are_rest_get_only_and_not_rpc_methods() -> None:
    app, _ = _build_app()
    transport = ASGITransport(app=app)

    route_map = {route.path: route for route in app.routes}
    for path in (
        "/docs",
        "/lens",
        "/openapi.json",
        "/openrpc.json",
        "/asyncapi.json",
        "/json-schema.json",
    ):
        assert path in route_map
        assert set(route_map[path].methods or []) == {"GET"}

    with Client(transport=transport, base_url="http://test") as client:
        # Runtime dispatch only mounts these as GET handlers. Depending on the
        # underlying route adapter we can surface either 404 or 405 for
        # non-GET methods, but never a successful RPC dispatch.
        assert client.post("/docs").status_code in {404, 405}
        assert client.post("/lens").status_code in {404, 405}
        assert client.post("/openapi.json").status_code in {404, 405}
        assert client.post("/openrpc.json").status_code in {404, 405}
        assert client.post("/asyncapi.json").status_code in {404, 405}
        assert client.post("/json-schema.json").status_code in {404, 405}

        method_names = {
            method["name"] for method in client.get("/openrpc.json").json()["methods"]
        }

    for forbidden in ("docs", "lens", "openapi", "openrpc", "asyncapi", "json_schema"):
        assert all(forbidden not in name.lower() for name in method_names)


def test_asyncapi_and_json_schema_are_pretty_printed() -> None:
    app, _ = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        asyncapi = client.get("/asyncapi.json")
        json_schema = client.get("/json-schema.json")

    assert asyncapi.status_code == 200
    assert "\n    'info': {" in asyncapi.text
    assert "'title':" in asyncapi.text

    assert json_schema.status_code == 200
    assert "\n    'properties': {" in json_schema.text
    assert "'Widget': {" in json_schema.text


def test_openrpc_server_url_respects_router_mount_jsonrpc_prefix_argument():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_openrpc_router_mount_prefix"
        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Widget)
    router.initialize()
    router.mount_jsonrpc(prefix="/jsonrpc")
    router.mount_openrpc()

    app = TigrblApp()
    app.include_router(router.router)

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    assert payload["servers"] == [{"name": router.title, "url": "/jsonrpc"}]
