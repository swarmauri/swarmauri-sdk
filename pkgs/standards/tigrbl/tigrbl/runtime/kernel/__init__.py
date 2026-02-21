from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from ...op.types import StepFn
from ..executor import _Ctx, _invoke
from .core import Kernel

_default_kernel = Kernel()


def get_cached_specs(model: type) -> Mapping[str, Any]:
    """Atoms can call this; zero per-request collection."""
    return _default_kernel.get_specs(model)


def build_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    return _default_kernel.build(model, alias)


async def run(
    model: type,
    alias: str,
    *,
    db: Any,
    request: Any | None = None,
    ctx: Optional[Mapping[str, Any]] = None,
) -> Any:
    phases = _default_kernel.build(model, alias)
    base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


__all__ = ["Kernel", "get_cached_specs", "_default_kernel", "build_phase_chains", "run"]
