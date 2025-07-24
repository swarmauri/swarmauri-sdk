"""
autoapi_hooks.py
Hook subsystem for AutoAPI – now includes the Phase enum and the
_Hook typing protocol, so nothing is missing.
"""

from enum import Enum, auto
from collections import defaultdict
from typing import Any, Dict, Protocol


# ───────────────────────── public types ─────────────────────────
class Phase(Enum):
    PRE_TX_BEGIN = auto()
    POST_HANDLER = auto()
    PRE_COMMIT = auto()
    POST_COMMIT = auto()
    POST_RESPONSE = auto()
    ON_ERROR = auto()


class _Hook(Protocol):
    async def __call__(self, ctx: Dict[str, Any]) -> None: ...


# ───────────────────────── helper API ───────────────────────────
def _init_hooks(self) -> None:
    """
    Injects a fresh registry into *self* and publishes
    `self.hook` / `self.register_hook` decorators.
    """
    self._hook_registry: Dict[Phase, Dict[str | None, list[_Hook]]] = defaultdict(
        lambda: defaultdict(list)
    )

    def _hook(
        phase: Phase,
        fn: _Hook | None = None,
        *,
        model: str | type | None = None,
        op: str | None = None,
    ):
        def _reg(f: _Hook) -> _Hook:
            async_f = (
                f
                if callable(getattr(f, "__await__", None))
                else (lambda ctx, f=f: f(ctx))  # sync-to-async shim
            )

            key: str | None
            if model is None and op is None:
                key = None
            elif model is not None and op is not None:
                name = model if isinstance(model, str) else model.__name__
                key = f"{name}.{op}"
            else:  # pragma: no cover - sanity guard
                raise ValueError("model and op must be provided together")

            self._hook_registry[phase][key].append(async_f)
            return f

        return _reg if fn is None else _reg(fn)

    # expose decorators on the instance
    self.hook = self.register_hook = _hook


async def _run(self, phase: Phase, ctx: Dict[str, Any]) -> None:
    """
    Fire hooks for *phase*.  First those bound to the specific
    RPC method (if any), then the catch-all hooks.
    """
    m = getattr(ctx.get("env"), "method", None)
    for fn in self._hook_registry[phase].get(m, []):
        await fn(ctx)
    for fn in self._hook_registry[phase].get(None, []):
        await fn(ctx)
