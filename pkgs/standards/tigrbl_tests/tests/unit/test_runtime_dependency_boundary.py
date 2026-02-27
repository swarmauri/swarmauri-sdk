from __future__ import annotations

import pytest

from tigrbl.runtime.dependencies import (
    DependencyToken,
    execute_dependency_tokens,
    execute_route_dependencies,
    invoke_dependency,
)


def test_dependency_token_constructor_is_removed() -> None:
    with pytest.raises(
        RuntimeError, match="Legacy dependency token execution has been removed"
    ):
        DependencyToken()


@pytest.mark.asyncio
async def test_route_dependency_execution_is_removed() -> None:
    with pytest.raises(
        RuntimeError, match="Legacy route dependency execution has been removed"
    ):
        await execute_route_dependencies(None, None, None)


@pytest.mark.asyncio
async def test_dependency_token_execution_is_removed() -> None:
    with pytest.raises(
        RuntimeError, match="Legacy dependency token execution has been removed"
    ):
        await execute_dependency_tokens(None, None, None)


@pytest.mark.asyncio
async def test_dependency_invocation_is_removed() -> None:
    with pytest.raises(
        RuntimeError, match="Legacy dependency invocation has been removed"
    ):
        await invoke_dependency(None)
