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
        method: str | None = None,
        model: str | None = None,
        verb: str | None = None,
    ):
        def _reg(f: _Hook) -> _Hook:
            async_f = (
                f
                if callable(getattr(f, "__await__", None))
                else (lambda ctx, f=f: f(ctx))  # sync-to-async shim
            )

            # Determine the hook key based on parameters
            hook_key = None
            if method is not None:
                # RPC method-based hook (backward compatibility)
                hook_key = method
            elif model is not None and verb is not None:
                # Model+verb based hook (new unified approach)
                hook_key = f"{model}.{verb}"
            elif model is not None:
                # Model-only hook (applies to all verbs for this model)
                hook_key = f"{model}.*"
            # If none specified, hook_key remains None (global hook)

            self._hook_registry[phase][hook_key].append(async_f)
            return f

        return _reg if fn is None else _reg(fn)

    # expose decorators on the instance
    self.hook = self.register_hook = _hook


async def _run(self, phase: Phase, ctx: Dict[str, Any]) -> None:
    """
    Fire hooks for *phase*.  Supports both RPC method-based hooks and
    model+verb based hooks for unified behavior across RPC, REST, and nested REST.
    """
    # Get context information
    method = None
    model = None
    verb = None

    # Extract method from RPC context (backward compatibility)
    if hasattr(ctx.get("env"), "method"):
        method = ctx.get("env").method

    # Extract model and verb from unified context
    if "model" in ctx and "verb" in ctx:
        model = ctx["model"]
        verb = ctx["verb"]

    # Run hooks in order of specificity:
    # 1. Method-specific hooks (RPC backward compatibility)
    if method:
        for fn in self._hook_registry[phase].get(method, []):
            await fn(ctx)

    # 2. Model+verb specific hooks
    if model and verb:
        hook_key = f"{model}.{verb}"
        for fn in self._hook_registry[phase].get(hook_key, []):
            await fn(ctx)

    # 3. Model-wide hooks (all verbs for this model)
    if model:
        hook_key = f"{model}.*"
        for fn in self._hook_registry[phase].get(hook_key, []):
            await fn(ctx)

    # 4. Global hooks (no specific method/model/verb)
    for fn in self._hook_registry[phase].get(None, []):
        await fn(ctx)


async def _invoke(self, model: str, verb: str, core_fn, *args, **kwargs) -> Any:
    """
    Unified invoke method that wraps any core function with the full hook lifecycle.
    This ensures parity between RPC, CRUD REST, and nested CRUD REST operations.

    Args:
        model: The model name (e.g., table name)
        verb: The operation verb (e.g., "create", "read", "update", "delete", "list", "clear")
        core_fn: The core function to execute
        *args, **kwargs: Arguments to pass to the core function

    Returns:
        The result of the core function execution
    """
    # Extract db from kwargs - it should always be present
    db = kwargs.get("db") or (args[-1] if args else None)
    if not db:
        raise ValueError(
            "Database session must be provided as 'db' kwarg or last positional arg"
        )

    # Build context
    ctx: Dict[str, Any] = {
        "model": model,
        "verb": verb,
        "db": db,
        "args": args,
        "kwargs": kwargs,
    }

    # Add request context if available (for REST endpoints)
    if "request" in kwargs:
        ctx["request"] = kwargs["request"]

    # Add env context if available (for RPC compatibility)
    if "env" in kwargs:
        ctx["env"] = kwargs["env"]

    try:
        # PRE_TX_BEGIN phase
        await self._run(Phase.PRE_TX_BEGIN, ctx)

        # Execute the core function (handle both sync and async)
        try:
            # Try calling as a no-arg function first (for closures/lambdas)
            result = core_fn()
            if hasattr(result, "__await__"):
                result = await result
        except TypeError:
            # If that fails, try with args/kwargs
            result = core_fn(*args, **kwargs)
            if hasattr(result, "__await__"):
                result = await result

        ctx["result"] = result

        # POST_HANDLER phase
        await self._run(Phase.POST_HANDLER, ctx)

        # Commit transaction if in transaction
        if hasattr(db, "in_transaction") and db.in_transaction():
            await self._run(Phase.PRE_COMMIT, ctx)
            if hasattr(db, "commit"):
                if hasattr(db.commit, "__await__"):
                    await db.commit()
                else:
                    db.commit()
            await self._run(Phase.POST_COMMIT, ctx)

        # POST_RESPONSE phase
        await self._run(Phase.POST_RESPONSE, ctx | {"response": result})

        return result

    except Exception as exc:
        # Rollback transaction
        if hasattr(db, "rollback"):
            if hasattr(db.rollback, "__await__"):
                await db.rollback()
            else:
                db.rollback()

        # ON_ERROR phase
        await self._run(Phase.ON_ERROR, ctx | {"error": exc})

        # Re-raise the exception
        raise
