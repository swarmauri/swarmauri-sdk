from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .core import Kernel


def build_kernelz_payload(kernel: "Kernel", app: Any):
    del kernel, app
    raise RuntimeError(
        "build_kernelz_payload has been fast-broken; use Kernel.compile_plan(app) instead."
    )
