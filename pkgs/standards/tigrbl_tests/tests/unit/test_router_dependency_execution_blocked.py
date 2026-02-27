import pytest

from tigrbl.requests import Request
from tigrbl import Router
from tigrbl.router._route import Route, compile_path
from tigrbl.security.dependencies import Dependency


@pytest.mark.asyncio
@pytest.mark.unit
async def test_router_does_not_invoke_route_level_dependencies() -> None:
    calls: list[str] = []

    def dep() -> str:
        calls.append("route-dep")
        return "route"

    def handler() -> dict[str, bool]:
        return {"ok": True}

    pattern, param_names = compile_path("/items")
    route = Route(
        methods=frozenset({"GET"}),
        path_template="/items",
        pattern=pattern,
        param_names=param_names,
        handler=handler,
        name="items",
        dependencies=[Dependency(dep)],
    )

    router = Router()
    request = Request(method="GET", path="/items")

    response = await router.call_handler(route, request)

    assert response.status_code == 200
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_router_does_not_invoke_parameter_dependency_defaults() -> None:
    calls: list[str] = []

    def dep() -> str:
        calls.append("param-dep")
        return "value"

    def handler(value: str = Dependency(dep)) -> dict[str, str | None]:
        return {"value": value}

    pattern, param_names = compile_path("/items")
    route = Route(
        methods=frozenset({"GET"}),
        path_template="/items",
        pattern=pattern,
        param_names=param_names,
        handler=handler,
        name="items",
    )

    router = Router()
    request = Request(method="GET", path="/items")

    response = await router.call_handler(route, request)

    assert response.status_code == 200
    assert calls == []
