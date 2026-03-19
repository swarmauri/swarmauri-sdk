from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.dep.extra import invoke_dependency as invoke_extra_dependency
from tigrbl_atoms.atoms.dep.security import (
    invoke_dependency as invoke_security_dependency,
)


class _Router:
    dependency_overrides: dict = {}
    dependency_overrides_provider = None


@dataclass(eq=True, unsafe_hash=False)
class _UnhashableDependency:
    value: str

    def __call__(self) -> str:
        return self.value


@pytest.mark.asyncio
async def test_extra_dependency_accepts_unhashable_callable_instance() -> None:
    router = _Router()
    req = SimpleNamespace(
        state=SimpleNamespace(_dependency_cleanups=[]),
        path_params={},
        query_params={},
    )
    dep = _UnhashableDependency("ok-extra")

    out = await invoke_extra_dependency(router, dep, req)

    assert out == "ok-extra"


@pytest.mark.asyncio
async def test_security_dependency_accepts_unhashable_callable_instance() -> None:
    router = _Router()
    req = SimpleNamespace(
        state=SimpleNamespace(_dependency_cleanups=[]),
        path_params={},
        query_params={},
    )
    dep = _UnhashableDependency("ok-security")

    out = await invoke_security_dependency(router, dep, req)

    assert out == "ok-security"
