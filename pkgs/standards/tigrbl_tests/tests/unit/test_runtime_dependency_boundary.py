from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl.router.resolve import resolve_handler_kwargs
from tigrbl.runtime.dependencies import (
    DependencyToken,
    execute_dependency_tokens,
    execute_route_dependencies,
)
from tigrbl.security.dependencies import Depends
from tigrbl.transport import Request


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
