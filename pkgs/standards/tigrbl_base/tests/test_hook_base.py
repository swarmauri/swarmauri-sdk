from tigrbl_atoms import HookPhase
from tigrbl_base._base._hook_base import HookBase
from tigrbl_core._spec.hook_spec import HookSpec


def step_fn(ctx: dict) -> dict:
    return ctx


def test_hook_base_fields_and_inheritance() -> None:
    hook = HookBase(phase=HookPhase.PRE_HANDLER, fn=step_fn, ops=("create",), order=10)

    assert isinstance(hook, HookSpec)
    assert hook.phase == HookPhase.PRE_HANDLER
    assert hook.fn is step_fn
    assert tuple(hook.ops) == ("create",)
    assert hook.order == 10
