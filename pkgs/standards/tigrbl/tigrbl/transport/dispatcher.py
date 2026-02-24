from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, MutableMapping, cast

from ..config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from ..runtime import executor as _executor
from ..runtime import trace as _trace
from ..op.types import PHASES

try:
    from ..runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
    from ..runtime.kernel import plan_labels as _kernel_plan_labels  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore
    _kernel_plan_labels = None  # type: ignore


@dataclass(frozen=True)
class OperationResolution:
    model: type
    alias: str
    target: str
    spec: Any | None


def _get_phase_chains(model: type, alias: str) -> Dict[str, Any]:
    if _kernel_build_phase_chains is not None:
        try:
            return _kernel_build_phase_chains(model, alias)
        except Exception:
            pass

    hooks_root = getattr(model, "hooks", None)
    alias_ns = getattr(hooks_root, alias, None) if hooks_root else None
    out: Dict[str, Any] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _resolve_model(router: Any, model_or_name: type | str) -> type:
    if isinstance(model_or_name, type):
        return model_or_name
    if router is None:
        raise LookupError(f"Unknown model '{model_or_name}'")
    mdl = getattr(router, "models", {}).get(model_or_name)
    if mdl is None:
        raise LookupError(f"Unknown model '{model_or_name}'")
    return mdl


def resolve_operation(
    *, router: Any, model_or_name: type | str, alias: str
) -> OperationResolution:
    model = _resolve_model(router, model_or_name)
    specs = getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {})
    sp_list = specs.get(alias) or ()
    sp = sp_list[0] if sp_list else None
    target = getattr(sp, "target", alias) or alias
    return OperationResolution(model=model, alias=alias, target=target, spec=sp)


async def dispatch_operation(
    *,
    router: Any,
    model_or_name: type | str,
    alias: str,
    payload: Any,
    db: Any,
    request: Any = None,
    ctx: Optional[Mapping[str, Any]] = None,
    response_serializer: Any = None,
    rpc_mode: bool = False,
) -> Any:
    resolution = resolve_operation(
        router=router, model_or_name=model_or_name, alias=alias
    )
    model = resolution.model
    if isinstance(ctx, MutableMapping):
        base_ctx = cast(Dict[str, Any], ctx)
    else:
        base_ctx = dict(ctx or {})
    base_ctx.setdefault("payload", payload if payload is not None else {})
    base_ctx.setdefault("db", db)
    if request is not None:
        base_ctx.setdefault("request", request)

    app_ref = (
        getattr(request, "app", None)
        or base_ctx.get("app")
        or base_ctx.get("router")
        or router
        or model
    )
    base_ctx.setdefault("router", router if router is not None else app_ref)
    base_ctx.setdefault("app", app_ref)
    base_ctx.setdefault("model", model)
    base_ctx.setdefault("op", alias)
    base_ctx.setdefault("method", alias)
    base_ctx.setdefault("target", resolution.target)
    base_ctx.setdefault(
        "env",
        SimpleNamespace(
            method=alias,
            params=base_ctx.get("payload"),
            target=resolution.target,
            model=model,
        ),
    )

    if request is not None:
        ac = getattr(getattr(request, "state", None), TIGRBL_AUTH_CONTEXT_ATTR, None)
        if ac is not None:
            base_ctx.setdefault("auth_context", ac)

    if callable(response_serializer):
        base_ctx["response_serializer"] = response_serializer

    phases = _get_phase_chains(model, alias)
    if rpc_mode:
        model_hooks = getattr(getattr(model, "hooks", None), alias, None)
        phases["POST_RESPONSE"] = list(getattr(model_hooks, "POST_RESPONSE", []) or [])

    try:
        if _kernel_plan_labels is not None:
            _trace.init(base_ctx, plan_labels=_kernel_plan_labels(model, alias))
        else:
            _trace.init(base_ctx)
    except Exception:
        pass

    return await _executor._invoke(request=request, db=db, phases=phases, ctx=base_ctx)


__all__ = ["OperationResolution", "dispatch_operation", "resolve_operation"]
