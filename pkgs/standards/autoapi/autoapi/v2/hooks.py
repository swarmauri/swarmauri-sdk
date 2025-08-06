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
        model: Union[str, type, None] = None,
        op: str | None = None,
    ):
        """
        Hook decorator supporting model and op parameters:

        Usage: @api.hook(Phase.POST_COMMIT, model="DeployKeys", op="create")
        Usage: @api.hook(Phase.POST_COMMIT, model=DeployKeys, op="create")
        Usage: @api.hook(Phase.POST_COMMIT)  # catch-all hook
        """

        def _reg(f: _Hook) -> _Hook:
            async_f = (
                f
                if callable(getattr(f, "__await__", None))
                else (lambda ctx, f=f: f(ctx))  # sync-to-async shim
            )

            # Determine the hook key based on parameters
            hook_key = None

            if model is not None and op is not None:
                # Model + op parameters
                if isinstance(model, str):
                    tab = model if model.endswith(("s", "S")) else f"{model}s"
                else:
                    tab = getattr(model, "__tablename__", model.__name__)
                if tab.islower():
                    model_name = "".join(part.title() for part in tab.split("_"))
                elif "_" in tab:
                    model_name = "".join(
                        part[:1].upper() + part[1:] for part in tab.split("_")
                    )
                else:
                    model_name = tab
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

    # expose decorators on the instance
    self.hook = self.register_hook = _hook


async def _run(self, phase: Phase, ctx: Dict[str, Any]) -> None:
    """Run hooks for *phase* in order and stop on the first error."""
    m = getattr(ctx.get("env"), "method", None)
    hooks = list(self._hook_registry[phase].get(m, []))
    hooks.extend(self._hook_registry[phase].get(None, []))
    for fn in hooks:
        await fn(ctx)
