"""Compatibility exports for legacy ``tigrbl_runtime.runtime.executor`` imports."""

from ...executors.invoke import _invoke
from ...executors.types import _Ctx

__all__ = ["_Ctx", "_invoke"]
