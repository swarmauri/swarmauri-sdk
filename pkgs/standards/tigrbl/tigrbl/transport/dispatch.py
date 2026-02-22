from __future__ import annotations

from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    MutableMapping,
    Sequence,
)

from ..config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from ..op.types import PHASES
from ..runtime import executor as _executor
from ..runtime.executor.types import _Ctx

try:
    from ..runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore


def resolve_model(router: Any, model_or_name: type | str) -> type | None:
    if isinstance(model_or_name, type):
        return model_or_name
    models: Dict[str, type] = getattr(router, "models", {}) or {}
    mdl = models.get(model_or_name)
    if mdl is not None:
        return mdl
    lower = str(model_or_name).lower()
    for key, value in models.items():
        if key.lower() == lower:
            return value
    return None


def resolve_target(model: type, alias: str) -> str:
    by_alias = getattr(getattr(model, "ops", None), "by_alias", {}) or {}
    specs = by_alias.get(alias) or ()
    if specs:
        return getattr(specs[0], "target", alias)
    return alias


def build_phase_chains(
    model: type, alias: str
) -> Dict[str, Sequence[Callable[..., Awaitable[Any]]]]:
    if _kernel_build_phase_chains is not None:
        return _kernel_build_phase_chains(model, alias)
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for phase in PHASES:
        out[phase] = list(getattr(alias_ns, phase, []) or [])
    return out


def build_ctx(
    *,
    router: Any,
    request: Any,
    db: Any,
    model: type,
    alias: str,
    target: str,
    payload: Any,
    path_params: Mapping[str, Any] | None = None,
    seed_ctx: Mapping[str, Any] | None = None,
    rpc_id: Any | None = None,
) -> MutableMapping[str, Any]:
    ctx: Dict[str, Any] = {}
    req_ctx = getattr(getattr(request, "state", None), "ctx", None)
    if isinstance(req_ctx, Mapping):
        ctx.update(req_ctx)
    if isinstance(seed_ctx, Mapping):
        ctx.update(seed_ctx)

    app_ref = getattr(request, "app", None) or router or model
    ctx.setdefault("request", request)
    ctx.setdefault("db", db)
    ctx.setdefault("payload", payload)
    ctx.setdefault("path_params", dict(path_params or {}))
    ctx.setdefault("app", app_ref)
    ctx.setdefault("api", router if router is not None else app_ref)
    ctx.setdefault("model", model)
    ctx.setdefault("op", alias)
    ctx.setdefault("method", alias)
    ctx.setdefault("target", target)
    ctx.setdefault(
        "env",
        SimpleNamespace(method=alias, params=payload, target=target, model=model),
    )
    if rpc_id is not None:
        ctx.setdefault("rpc_id", rpc_id)

    auth_context = getattr(
        getattr(request, "state", None), TIGRBL_AUTH_CONTEXT_ATTR, None
    )
    if auth_context is not None:
        ctx["auth_context"] = auth_context
    return _Ctx(ctx)


def resolve_operation(
    router: Any, model_or_name: type | str, alias: str, *, strict: bool = False
) -> tuple[type, str]:
    model = resolve_model(router, model_or_name)
    if model is None:
        raise LookupError(f"Unknown model '{model_or_name}'")
    by_alias = getattr(getattr(model, "ops", None), "by_alias", {}) or {}
    if alias not in by_alias:
        if strict:
            model_name = getattr(model, "__name__", model)
            raise LookupError(f"Unknown operation '{alias}' for model '{model_name}'")
        return model, alias
    return model, resolve_target(model, alias)


async def dispatch_operation(
    *,
    router: Any,
    request: Any,
    db: Any,
    model_or_name: type | str,
    alias: str,
    payload: Any,
    target: str | None = None,
    path_params: Mapping[str, Any] | None = None,
    seed_ctx: Mapping[str, Any] | None = None,
    response_serializer: Callable[[Any], Any] | None = None,
    rpc_id: Any | None = None,
    rpc_mode: bool = False,
) -> Any:
    model, resolved_target = resolve_operation(router, model_or_name, alias)
    if target is not None:
        resolved_target = target
    ctx = build_ctx(
        router=router,
        request=request,
        db=db,
        model=model,
        alias=alias,
        target=resolved_target,
        payload=payload,
        path_params=path_params,
        seed_ctx=seed_ctx,
        rpc_id=rpc_id,
    )
    if callable(response_serializer):
        ctx["response_serializer"] = response_serializer

    phases = build_phase_chains(model, alias)
    if rpc_mode:
        model_hooks = getattr(getattr(model, "hooks", None), alias, None)
        phases["POST_RESPONSE"] = list(getattr(model_hooks, "POST_RESPONSE", []) or [])

    return await _executor._invoke(request=request, db=db, phases=phases, ctx=ctx)


__all__ = [
    "build_ctx",
    "build_phase_chains",
    "dispatch_operation",
    "resolve_model",
    "resolve_operation",
    "resolve_target",
]
