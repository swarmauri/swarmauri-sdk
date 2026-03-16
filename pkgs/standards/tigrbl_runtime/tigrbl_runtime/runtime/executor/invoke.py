"""Runtime invoke facade for operation execution."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

from tigrbl_runtime.executors.invoke import _invoke
from tigrbl_runtime.runtime.kernel import build_phase_chains


def resolve_phase_chains(model: type, alias: str) -> Mapping[str, list[Any]]:
    """Resolve executable phase chains for a model operation."""
    return build_phase_chains(model, alias) or {}


async def invoke_op(
    *,
    request: Any = None,
    db: Any = None,
    model: type,
    alias: str,
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Resolve phases and execute an operation through runtime invocation."""
    return await _invoke(
        request=request,
        db=db,
        phases=resolve_phase_chains(model, alias),
        ctx=ctx,
    )


__all__ = ["_invoke", "resolve_phase_chains", "invoke_op"]
