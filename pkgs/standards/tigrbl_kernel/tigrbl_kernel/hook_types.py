"""Kernel-owned hook type definitions.

The kernel compiles plans and phase chains, but does not execute them.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

StepFn = Callable[[Any], Awaitable[Any] | Any]

__all__ = ["StepFn"]
