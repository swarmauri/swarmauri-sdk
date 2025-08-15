# autoapi/v3/bindings/rpc.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from pydantic import BaseModel

from ..opspec import OpSpec
from ..opspec.types import PHASES
from ..runtime import executor as _executor  # expects _invoke(request, db, phases, ctx)

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ns(obj: Any, name: str) -> Any:
    ns = getattr(obj, name, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(obj, name, ns)
    return ns


def _get_phase_chains(
    model: type, alias: str
) -> Dict[str, Sequence[Callable[..., Awaitable[Any]]]]:
    """
    Build the mapping { phase_name: [step, ...], ... } expected by the executor.
    Missing phases become empty lists.
    """
    hooks_root = _ns(model, "hooks")
    alias_ns = getattr(hooks_root, alias, None)
    if alias_ns is None:
        return {ph: [] for ph in PHASES}

    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _coerce_payload(payload: Any) -> Mapping[str, Any]:
    """
    Accept dict-like or Pydantic models; fallback to {} for None.
    """
    if payload is None:
        return {}
    if isinstance(payload, BaseModel):
        try:
            return payload.model_dump(exclude_none=False)
        except Exception:
            return dict(payload.__dict__)
    if isinstance(payload, Mapping):
        return dict(payload)
    return {}  # unexpected shapes → ignore


def _validate_input(
    model: type, alias: str, target: str, payload: Mapping[str, Any]
) -> Mapping[str, Any]:
    """
    Choose the appropriate request schema (if any) and validate/normalize payload.
    • Use .schemas.<alias>.in_ when present.
    • For list/clear, prefer .schemas.<alias>.list.
    """
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return payload
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return payload

    in_model = getattr(alias_ns, "in_", None)
    if target in {"list", "clear"}:
        in_model = getattr(alias_ns, "list", in_model)

    if in_model and inspect.isclass(in_model) and issubclass(in_model, BaseModel):
        try:
            inst = in_model.model_validate(payload)  # type: ignore[arg-type]
            return inst.model_dump(exclude_none=True)
        except Exception as e:
            # Let the executor/runtime error mappers standardize later; pass original payload
            logger.debug(
                "rpc input validation failed for %s.%s: %s",
                model.__name__,
                alias,
                e,
                exc_info=True,
            )
    return payload


def _serialize_output(
    model: type, alias: str, target: str, sp: OpSpec, result: Any
) -> Any:
    """
    If the op returns 'model' and we have an OUT schema, serialize result(s).
    For 'list', OUT schema represents the element shape.
    """
    if sp.returns != "model":
        return result

    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return result
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return result

    out_model = getattr(alias_ns, "out", None)
    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return result

    try:
        if target == "list" and isinstance(result, (list, tuple)):
            return [
                out_model.model_validate(x).model_dump(exclude_none=True)
                for x in result
            ]
        # Single object case
        return out_model.model_validate(result).model_dump(exclude_none=True)
    except Exception as e:
        # If serialization fails, let raw result through rather than failing the call
        logger.debug(
            "rpc output serialization failed for %s.%s: %s",
            model.__name__,
            alias,
            e,
            exc_info=True,
        )
        return result


# ───────────────────────────────────────────────────────────────────────────────
# RPC wrapper builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_rpc_callable(model: type, sp: OpSpec) -> Callable[..., Awaitable[Any]]:
    """
    Create an async callable that:
      1) validates payload (if schema present),
      2) runs the executor with the model's phase chains,
      3) serializes the result to the expected return form.
    Signature:
        async def rpc_method(payload: Mapping | BaseModel | None = None, *, db, request=None, ctx=None) -> Any
    """
    alias = sp.alias
    target = sp.target

    async def _rpc_method(
        payload: Any = None,
        *,
        db: Any,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        # 1) normalize + validate input
        raw_payload = _coerce_payload(payload)
        norm_payload = _validate_input(model, alias, target, raw_payload)

        # 2) build executor context & phases
        base_ctx: Dict[str, Any] = dict(ctx or {})
        base_ctx.setdefault("payload", norm_payload)
        base_ctx.setdefault("db", db)
        if request is not None:
            base_ctx.setdefault("request", request)
        # helpful env metadata
        base_ctx.setdefault(
            "env",
            SimpleNamespace(
                method=alias, params=norm_payload, target=target, model=model
            ),
        )

        phases = _get_phase_chains(model, alias)

        # 3) run executor + shape output
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=base_ctx,
        )

        return _serialize_output(model, alias, target, sp, result)

    # Give the callable a nice name for introspection/logging
    _rpc_method.__name__ = f"rpc_{model.__name__}_{alias}"
    _rpc_method.__qualname__ = _rpc_method.__name__
    _rpc_method.__doc__ = f"RPC method for {model.__name__}.{alias} ({target})"

    return _rpc_method


def _attach_one(model: type, sp: OpSpec) -> None:
    rpc_root = _ns(model, "rpc")
    fn = _build_rpc_callable(model, sp)
    setattr(rpc_root, sp.alias, fn)
    logger.debug("rpc: %s.%s registered", model.__name__, sp.alias)


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def register_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Register async callables under `model.rpc.<alias>` for each OpSpec.
    If `only_keys` is provided, limit work to those (alias,target) pairs.
    """
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["register_and_attach"]
