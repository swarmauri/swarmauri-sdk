from __future__ import annotations

from typing import Any

from .invoke import _invoke
from .types import _Ctx


async def _run(
    self,
    model: type,
    alias: str,
    *,
    db: Any,
    request: Any | None = None,
    ctx: Any | None = None,
) -> Any:
    phases = self._build_op(model, alias)
    base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


async def _run_phase_chain(self, ctx: _Ctx, phases: Any) -> None:
    for _phase, steps in (phases or {}).items():
        ctx.phase = _phase
        for step in steps or ():
            rv = step(ctx)
            if hasattr(rv, "__await__"):
                await rv
