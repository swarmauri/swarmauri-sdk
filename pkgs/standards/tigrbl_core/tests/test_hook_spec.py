from __future__ import annotations

from tigrbl_core._spec.hook_spec import HookSpec, OpHook


def test_hook_spec_alias_points_to_same_type() -> None:
    assert OpHook is HookSpec


def test_hook_spec_stores_hook_metadata() -> None:
    hook = HookSpec(phase="pre", fn=lambda ctx: ctx, order=10, name="run")

    assert hook.phase == "pre"
    assert hook.order == 10
    assert hook.name == "run"
