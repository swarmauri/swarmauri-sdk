import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblRouter, TigrblApp, op_alias, op_ctx


async def _get_json(app, path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    return response


def _find_get_route_path(app: TigrblApp, alias: str) -> str:
    return next(
        route.path
        for route in app.router.routes
        if route.path.endswith(f"/{alias}") and "GET" in (route.methods or set())
    )


@pytest.mark.xfail(reason="TigrblRouter does not expose HTTP method decorators")
def test_tigrbl_router_is_asgi_compatible():
    """TigrblRouter should serve routes as an ASGI app."""
    router = TigrblRouter()

    @router.get("/health")
    def health():
        return {"ok": True}

    import asyncio

    response = asyncio.run(_get_json(router, "/health"))

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_tigrbl_app_op_alias_declares_operation():
    """`op_alias` declares a custom operation on the app class."""

    @op_alias(alias="health", target="custom", http_methods=("GET",))
    class HealthApp(TigrblApp):
        pass

    spec = HealthApp.__tigrbl_ops__[-1]
    assert spec.alias == "health"
    assert spec.target == "custom"
    assert spec.http_methods == ("GET",)


def test_tigrbl_app_op_ctx_binds_handler():
    """`op_ctx` binds a ctx handler onto the app class."""

    class CtxOnlyApp(TigrblApp):
        pass

    @op_ctx(alias="health", target="custom", bind=CtxOnlyApp)
    def health(_cls, _ctx):
        return {"ok": True}

    bound = CtxOnlyApp.__dict__["health"]
    assert isinstance(bound, classmethod)
    assert bound.__func__.__tigrbl_op_decl__.alias == "health"
    assert bound.__func__.__tigrbl_op_decl__.target == "custom"


def test_tigrbl_app_is_asgi_compatible_with_op_alias_and_op_ctx():
    """TigrblApp should serve op_alias/op_ctx routes as an ASGI app."""

    @op_alias(alias="health", target="custom", http_methods=("GET",))
    class HealthApp(TigrblApp):
        pass

    @op_ctx(alias="health", target="custom", bind=HealthApp)
    def health(_cls, _ctx):
        return {"ok": True}

    app = HealthApp()
    health_path = _find_get_route_path(app, "health")

    import asyncio

    response = asyncio.run(_get_json(app, health_path))

    assert response.status_code == 200
    assert response.json() == {"ok": True}
