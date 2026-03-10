from __future__ import annotations

from typing import Any, Dict, List, Mapping

from tigrbl_atoms import StepFn
from .core import Kernel
from .models import OpView, PackedKernel, SchemaIn, SchemaOut

_default_kernel = Kernel()


def get_cached_specs(model: type) -> Mapping[str, Any]:
    return _default_kernel.get_specs(model)


def build_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    return _default_kernel._build_op(model, alias)


def build_kernel_plan(app: Any):
    return _default_kernel.kernel_plan(app)


def build_packed_kernel(app: Any) -> PackedKernel | None:
    return _default_kernel.kernel_plan(app).packed


def plan_labels(model: type, alias: str) -> list[str]:
    return _default_kernel._plan_labels(model, alias)


__all__ = [
    "Kernel",
    "OpView",
    "PackedKernel",
    "SchemaIn",
    "SchemaOut",
    "build_kernel_plan",
    "build_packed_kernel",
    "get_cached_specs",
    "_default_kernel",
    "build_phase_chains",
    "plan_labels",
]
