"""Compatibility exports for legacy ``tigrbl_runtime.runtime.executor`` imports."""

from tigrbl_runtime.executors.invoke import _invoke
from tigrbl_runtime.executors.types import _Ctx

__all__ = ["_Ctx", "_invoke"]
