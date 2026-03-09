from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_typing.status.mappings import status

from tigrbl_atoms.atoms.dep import REGISTRY
from tigrbl_atoms.atoms.dep import extra, security
from tigrbl_atoms.types import Atom, GuardedCtx, PlannedCtx


def test_dep_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("dep", "security"), ("dep", "extra")}


def test_dep_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("dep", "security")] == (security.ANCHOR, security.INSTANCE)
    assert REGISTRY[("dep", "extra")] == (extra.ANCHOR, extra.INSTANCE)


def test_dep_instances_and_impls_use_atom_contract() -> None:
    assert isinstance(security.INSTANCE, Atom)
    assert isinstance(extra.INSTANCE, Atom)
    assert issubclass(security.AtomImpl, Atom)
    assert issubclass(extra.AtomImpl, Atom)
    assert security.INSTANCE.name == "dep.security"
    assert extra.INSTANCE.name == "dep.extra"
    assert security.INSTANCE.anchor == security.ANCHOR
    assert extra.INSTANCE.anchor == extra.ANCHOR


def test_dep_security_instance_promotes_planned_ctx_to_guarded_ctx() -> None:
    ctx = PlannedCtx()

    out = asyncio.run(security.INSTANCE(lambda: "ok", ctx))

    assert isinstance(out, GuardedCtx)


def test_dep_extra_instance_preserves_guarded_ctx_shape() -> None:
    ctx = GuardedCtx()

    out = asyncio.run(extra.INSTANCE(lambda: "ok", ctx))

    assert isinstance(out, GuardedCtx)


def test_dep_security_run_injects_request_into_dependency_function() -> None:
    req = SimpleNamespace(
        path_params={"id": "7"},
        query_params={},
        headers={},
        state=SimpleNamespace(_dependency_cleanups=[]),
    )
    router = SimpleNamespace(dependency_overrides={})

    def dep(request: object) -> str:
        assert request is req
        return request.path_params["id"]

    ctx = SimpleNamespace(request=req, router=router)

    out = asyncio.run(security._run(dep, ctx))

    assert out == "7"


def test_dep_security_run_raises_401_when_required_auth_is_missing() -> None:
    req = SimpleNamespace(
        path_params={},
        query_params={},
        headers={},
        state=SimpleNamespace(_dependency_cleanups=[]),
    )
    router = SimpleNamespace(dependency_overrides={})

    def dep() -> None:
        return None

    dep.__tigrbl_require_auth__ = True

    with pytest.raises(HTTPException) as exc:
        asyncio.run(security._run(dep, SimpleNamespace(request=req, router=router)))

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
