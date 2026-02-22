import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblRouter, TigrblApp
from tigrbl.security.dependencies import Dependency


class StatusDetailError(Exception):
    def __init__(
        self, status_code: int, detail: str, headers: dict[str, str] | None = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


@pytest.mark.unit
def test_router_exposes_event_alias_lists() -> None:
    app = TigrblApp()

    def startup_handler() -> None:
        return None

    def shutdown_handler() -> None:
        return None

    app.add_event_handler("startup", startup_handler)
    app.add_event_handler("shutdown", shutdown_handler)

    assert app.on_startup is app.event_handlers["startup"]
    assert app.on_shutdown is app.event_handlers["shutdown"]
    assert app.on_startup == [startup_handler]
    assert app.on_shutdown == [shutdown_handler]


@pytest.mark.asyncio
@pytest.mark.xfail(
    raises=AttributeError,
    reason="TigrblApp no longer exposes REST verb decorator helpers such as .get.",
)
async def test_dependency_overrides_provider_is_applied_during_resolution() -> None:
    app = TigrblApp()

    def get_token() -> str:
        return "original"

    @app.get("/token")
    def token(value: str = Dependency(get_token)) -> dict[str, str]:
        return {"value": value}

    app.dependency_overrides[get_token] = lambda: "override"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/token")

    assert response.status_code == 200
    assert response.json() == {"value": "override"}


@pytest.mark.asyncio
@pytest.mark.xfail(
    raises=AttributeError,
    reason="TigrblRouter no longer exposes REST verb decorator helpers such as .get.",
)
async def test_framework_http_exception_is_translated_to_json_response() -> None:
    router = TigrblRouter()

    @router.get("/boom")
    def boom() -> None:
        raise StatusDetailError(status_code=418, detail="teapot")

    async with AsyncClient(
        transport=ASGITransport(app=router), base_url="http://test"
    ) as client:
        response = await client.get("/boom")

    assert response.status_code == 418
    assert response.json() == {"detail": "teapot"}
