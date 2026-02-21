from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional, Sequence

from ..config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from ..runtime import executor as _executor
from ..runtime.executor.types import _Ctx
from ..bindings.rest.helpers import _get_phase_chains


def resolve_model(api: Any, model_name: str) -> Optional[type]:
    models: Dict[str, type] = getattr(api, "models", {}) or {}
    model = models.get(model_name)
    if model is not None:
        return model
    lowered = model_name.lower()
    for key, value in models.items():
        if key.lower() == lowered:
            return value
    return None


def resolve_target(model: type, alias: str, default: str = "custom") -> str:
    by_alias = getattr(getattr(model, "ops", None), "by_alias", {}) or {}
    spec = by_alias.get(alias)
    if spec is None:
        raise KeyError(
            f"Unknown operation alias '{alias}' for model {getattr(model, '__name__', model)!r}"
        )
    return getattr(spec, "target", default)


def make_ctx(
    *,
    request: Any,
    db: Any,
    api: Any,
    model: type,
    alias: str,
    target: str,
    payload: Any,
    path_params: Mapping[str, Any] | None = None,
    seed: Optional[MutableMapping[str, Any]] = None,
) -> _Ctx:
    base: Dict[str, Any] = dict(seed or {})
    app_ref = getattr(request, "app", None)
    base.setdefault("request", request)
    base.setdefault("db", db)
    base.setdefault("payload", payload)
    base.setdefault("path_params", dict(path_params or {}))
    base.setdefault("api", api if api is not None else app_ref)
    base.setdefault("app", app_ref)
    base.setdefault("model", model)
    base.setdefault("op", alias)
    base.setdefault("method", alias)
    base.setdefault("target", target)
    base.setdefault(
        "env",
        SimpleNamespace(method=alias, params=payload, target=target, model=model),
    )
    ac = getattr(getattr(request, "state", object()), TIGRBL_AUTH_CONTEXT_ATTR, None)
    if ac is not None:
        base.setdefault("auth_context", ac)
    return _Ctx(base)


async def dispatch_operation(
    *,
    request: Any,
    db: Any,
    api: Any,
    alias: str,
    payload: Any,
    model: type | None = None,
    model_name: str | None = None,
    target: str | None = None,
    path_params: Mapping[str, Any] | None = None,
    ctx_seed: Optional[MutableMapping[str, Any]] = None,
    response_serializer: Callable[[Any], Any] | None = None,
    post_response_steps: Sequence[Callable[..., Any]] | None = None,
) -> Any:
    selected_model = model
    if selected_model is None:
        if not model_name:
            raise KeyError("model_name is required when model is not provided")
        selected_model = resolve_model(api, model_name)
    if selected_model is None:
        raise KeyError(f"Unknown model '{model_name}'")

    if target is None:
        effective_target = resolve_target(selected_model, alias)
    else:
        effective_target = target
    ctx = make_ctx(
        request=request,
        db=db,
        api=api,
        model=selected_model,
        alias=alias,
        target=effective_target,
        payload=payload,
        path_params=path_params,
        seed=ctx_seed,
    )
    if response_serializer is not None:
        ctx["response_serializer"] = response_serializer

    phases = _get_phase_chains(selected_model, alias)
    if post_response_steps is not None:
        phases["POST_RESPONSE"] = list(post_response_steps)

    return await _executor._invoke(request=request, db=db, phases=phases, ctx=ctx)


__all__ = ["dispatch_operation", "make_ctx", "resolve_model", "resolve_target"]
