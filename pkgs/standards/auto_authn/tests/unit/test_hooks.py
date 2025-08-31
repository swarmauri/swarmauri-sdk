"""Unit tests for auto_authn.hooks module.

Ensure the registration helper wires the injection hook and populates
principal fields in the context.
"""

from types import SimpleNamespace

import pytest

from auto_authn.hooks import register_inject_hook
from autoapi.v3 import PHASE


class DummyAPI:
    """Minimal API stub capturing registered hooks."""

    def __init__(self) -> None:
        self.hooks = {}

    def register_hook(self, phase):
        def decorator(func):
            self.hooks[phase] = func
            return func

        return decorator


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_inject_hook_injects_principal():
    """Hook registers for PRE_TX_BEGIN and injects tenant/user IDs."""
    api = DummyAPI()
    register_inject_hook(api)

    phase = PHASE.PRE_TX_BEGIN
    assert phase in api.hooks

    request = SimpleNamespace(
        state=SimpleNamespace(principal={"tid": "t1", "sub": "u1"})
    )
    ctx = {"request": request}

    await api.hooks[phase](ctx)

    assert ctx["__autoapi_injected_fields__"] == {"tenant_id": "t1", "user_id": "u1"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_inject_hook_accepts_object_principal():
    """Hook handles principals implementing attribute access."""
    api = DummyAPI()
    register_inject_hook(api)

    phase = PHASE.PRE_TX_BEGIN
    request = SimpleNamespace(
        state=SimpleNamespace(principal=SimpleNamespace(tenant_id="t1", user_id="u1"))
    )
    ctx = {"request": request}

    await api.hooks[phase](ctx)

    assert ctx["__autoapi_injected_fields__"] == {"tenant_id": "t1", "user_id": "u1"}
