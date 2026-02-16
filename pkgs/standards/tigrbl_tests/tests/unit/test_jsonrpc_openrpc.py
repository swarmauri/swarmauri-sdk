from httpx import ASGITransport, Client
from sqlalchemy import Column, String
from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk


def _build_app():
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openrpc"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
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

        create_method = methods[f"{model.__name__}.create"]
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
    assert data["id"] == 1
    assert "error" not in data
    assert data["result"]["name"] == "New Widget"


def test_mount_lens_uses_latest_openrpc_path_by_default() -> None:
    app, _ = _build_app()
    app.mount_openrpc(path="/schema/openrpc.json")
    app.mount_lens(path="/lens-custom")

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        html = client.get("/lens-custom").text

    assert "/schema/openrpc.json" in html
def test_openrpc_server_url_respects_api_mount_jsonrpc_prefix_argument():
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openrpc_api_mount_prefix"
        name = Column(String, nullable=False)

    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()
    api.mount_jsonrpc(prefix="/jsonrpc")
    api.mount_openrpc()

    transport = ASGITransport(app=api)
    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    assert payload["servers"] == [{"name": api.title, "url": "/jsonrpc"}]
