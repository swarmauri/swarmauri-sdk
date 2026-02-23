from httpx import ASGITransport, Client
from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_rpc_options"
    name = Column(String, nullable=False)


def _build_app() -> TigrblApp:
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app


def test_rpc_options_is_handled_without_dispatch_body() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        response = client.options("/rpc")

    assert response.status_code == 204
    assert response.text == ""
    assert response.headers["allow"] == "OPTIONS,POST"
    assert response.headers["access-control-allow-methods"] == "OPTIONS,POST"


def test_rpc_options_returns_cors_preflight_headers() -> None:
    app = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        response = client.options(
            "/rpc",
            headers={
                "Origin": "https://frontend.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

    assert response.status_code == 204
    assert response.headers["access-control-allow-origin"] == "https://frontend.example"
    assert (
        response.headers["access-control-allow-headers"] == "authorization,content-type"
    )
    assert response.headers["vary"] == "origin,access-control-request-headers"
