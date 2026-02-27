from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from tigrbl.runtime.dependencies import (
    DependencyToken,
    execute_dependency_tokens,
    execute_route_dependencies,
)
from tigrbl import Depends
from tigrbl import Request


async def resolve_handler_kwargs(_router: SimpleNamespace, route: SimpleNamespace, _req: Request) -> dict[str, object]:
    kwargs: dict[str, object] = {}
    signature = inspect.signature(route.handler)
    for name, param in signature.parameters.items():
        kwargs[name] = param.default
    return kwargs


@pytest.mark.asyncio
async def test_resolution_does_not_execute_dependencies() -> None:
    calls: list[str] = []

    def dep() -> str:
        calls.append("dep")
        return "ok"

    def handler(value: str = Depends(dep)) -> dict[str, str]:
        return {"value": value}

    route = SimpleNamespace(handler=handler, dependencies=[])
    req = Request(method="GET", path="/items")

    kwargs = await resolve_handler_kwargs(SimpleNamespace(), route, req)

    assert isinstance(kwargs["value"], DependencyToken)
    assert calls == []

    executed = await execute_dependency_tokens(SimpleNamespace(), kwargs, req)
    assert executed["value"] == "ok"
    assert calls == ["dep"]


@pytest.mark.asyncio
async def test_route_dependencies_execute_in_runtime_phase() -> None:
    calls: list[str] = []

    def dep() -> str:
        calls.append("route")
        return "ok"

    route = SimpleNamespace(handler=lambda: {"ok": True}, dependencies=[Depends(dep)])

    router = SimpleNamespace(_is_metadata_route=lambda _route: False)
    req = Request(method="GET", path="/items")

    await execute_route_dependencies(router, route, req)
    assert calls == ["route"]
