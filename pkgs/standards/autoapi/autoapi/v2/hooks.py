"""
autoapi_hooks.py
Hook subsystem for AutoAPI – now includes the Phase enum and the
_Hook typing protocol, so nothing is missing.
"""

from enum import Enum, auto
from collections import defaultdict
from typing import Any, Dict, Protocol, Union


# ───────────────────────── public types ─────────────────────────
class Phase(Enum):
    # Pre-transaction (no DB tx yet)
    PRE_TX_BEGIN = auto()

    # Inside an open DB transaction
    PRE_HANDLER = auto()
    POST_HANDLER = auto()
    PRE_COMMIT = auto()
    POST_COMMIT = auto()

    # After the result has been assembled (non-fatal by design)
    POST_RESPONSE = auto()

    # Rollback + granular error phases
    ON_ROLLBACK = auto()

    ON_PRE_HANDLER_ERROR = auto()
    ON_HANDLER_ERROR = auto()
    ON_POST_HANDLER_ERROR = auto()
    ON_PRE_COMMIT_ERROR = auto()
    ON_COMMIT_ERROR = auto()
    ON_POST_COMMIT_ERROR = auto()
    ON_POST_RESPONSE_ERROR = auto()

    # Generic catch-all
    ON_ERROR = auto()

    # Finally
    FINAL = auto()


class _Hook(Protocol):
    async def __call__(self, ctx: Dict[str, Any]) -> None: ...


# ───────────────────────── helper API ───────────────────────────
def _init_hooks(self) -> None:
    """
    Injects a fresh registry into *self* and publishes
    a `self.register_hook` decorator.
    """
    self._hook_registry: Dict[Phase, Dict[str | None, list[_Hook]]] = defaultdict(
        lambda: defaultdict(list)
    )

    def _hook(
        phase: Phase,
        fn: _Hook | None = None,
        *,
        model: Union[str, type, None] = None,
        op: str | None = None,
    ):
        """
        Hook decorator supporting model and op parameters:

        Usage: @api.register_hook(Phase.POST_COMMIT, model="DeployKey", op="create")
        Usage: @api.register_hook(Phase.POST_COMMIT, model=DeployKey, op="create")
        Usage: @api.register_hook(Phase.POST_COMMIT)  # catch-all hook
        """

        def _reg(f: _Hook) -> _Hook:
            async def _async_wrapper(ctx, _f=f):
                result = _f(ctx)
                if callable(getattr(result, "__await__", None)):
                    return await result
                return result

            async_f = f if callable(getattr(f, "__await__", None)) else _async_wrapper

            # Preserve the original function name for registry visibility
            async_f.__name__ = getattr(f, "__name__", repr(f))
            async_f.__qualname__ = getattr(f, "__qualname__", async_f.__name__)

            # Determine the hook key based on parameters
            hook_key = None

            if model is not None and op is not None:
                # Model + op parameters
                if isinstance(model, str):
                    if hasattr(self, "models") and hasattr(self.models, model):
                        model_name = getattr(self.models, model).__name__
                    else:
                        model_name = model
                else:
                    model_name = getattr(model, "__name__", repr(model))
                hook_key = f"{model_name}.{op}"
            elif model is not None or op is not None:
                # Error: both model and op must be provided together
                raise ValueError(
                    "Both 'model' and 'op' parameters must be provided together"
                )
            # If neither model nor op is provided, hook_key remains None (catch-all)

            # Register the hook
            self._hook_registry[phase][hook_key].append(async_f)
            return f

        return _reg if fn is None else _reg(fn)

    # expose decorator on the instance
    self.register_hook = _hook


async def _run(self, phase: Phase, ctx: Dict[str, Any]) -> None:
    """Run hooks for *phase* in order and stop on the first error."""
    m = getattr(ctx.get("env"), "method", None)
    hooks = list(self._hook_registry[phase].get(None, []))
    hooks.extend(self._hook_registry[phase].get(m, []))
    for fn in hooks:
        await fn(ctx)
