"""Kernel-owned hook type definitions.

The kernel compiles plans and phase chains, but does not execute them.
"""

from __future__ import annotations

from tigrbl_atoms import HookPhase, HookPhases, StepFn

__all__ = ["HookPhase", "HookPhases", "StepFn"]
