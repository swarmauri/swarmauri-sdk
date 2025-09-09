# tigrbl/v3/bindings/rpc.py
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

from ..op import OpSpec
from ..op.types import PHASES
from ..runtime import executor as _executor  # expects _invoke(request, db, phases, ctx)

# Prefer Kernel phase-chains if available (atoms + system steps + hooks)
try:
    from ..runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rpc")

_Key = Tuple[str, str]  # (alias, target)


# Mapping with attribute-style access
class AttrDict(dict):
    def __getattr__(self, item: str) -> Any:  # pragma: no cover - trivial
        try:
            return self[item]
        except KeyError as e:  # pragma: no cover - debug helper
            raise AttributeError(item) from e


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
    Prefer building via runtime Kernel (atoms + system steps + hooks in one lifecycle).
    Fallback: read the pre-built model.hooks.<alias> chains directly.
    """
    if _kernel_build_phase_chains is not None:
        try:
            return _kernel_build_phase_chains(model, alias)
        except Exception:
            logger.exception(
                "Kernel build_phase_chains failed for %s.%s; falling back to hooks",
                getattr(model, "__name__", model),
                alias,
            )
    hooks_root = _ns(model, "hooks")
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _coerce_payload(payload: Any) -> Any:
    """Normalize common payload shapes.

    ``dict``-like and Pydantic models become plain ``dict``s. ``None`` becomes an
    empty ``dict``. Sequence payloads (used by bulk operations) pass through as
    lists of ``dict``s when possible; otherwise the original sequence is
    returned. Any other type yields an empty ``dict``.
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
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        out: list[Any] = []
        for item in payload:
            if isinstance(item, Mapping):
                out.append(dict(item))
            else:
                out.append(item)
        return out
    return {}


def _ensure_jsonable(obj: Any) -> Any:
    """Best-effort conversion of DB rows or ORM objects to primitives."""
    if isinstance(obj, (list, tuple)):
        return [_ensure_jsonable(x) for x in obj]
    if isinstance(obj, Mapping):
        try:
            return AttrDict({k: _ensure_jsonable(v) for k, v in dict(obj).items()})
        except Exception:
            pass
    try:
        data = vars(obj)
    except TypeError:
        return obj
    return AttrDict(
        {k: _ensure_jsonable(v) for k, v in data.items() if not k.startswith("_")}
    )


def _validate_input(
    model: type, alias: str, target: str, payload: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Choose the appropriate request schema (if any) and validate/normalize payload."""
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return payload
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return payload

    in_model = getattr(alias_ns, "in_", None)

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


def _serialize_output(model: type, alias: str, target: str, result: Any) -> Any:
    """Serialize result(s) if an OUT schema is available for the op.

    For 'list', the OUT schema represents the element shape.
    """
    schemas_root = getattr(model, "schemas", None)
    if not schemas_root:
        return _ensure_jsonable(result)
    alias_ns = getattr(schemas_root, alias, None)
    if not alias_ns:
        return _ensure_jsonable(result)

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        out_model = getattr(alias_ns, "out_item", None)
    else:
        out_model = getattr(alias_ns, "out", None)

    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return _ensure_jsonable(result)

    try:
        if target == "list" and isinstance(result, (list, tuple)):
            return [
                out_model.model_validate(x).model_dump(
                    exclude_none=False, by_alias=True
                )
                for x in result
            ]
        if target in {
            "bulk_create",
            "bulk_update",
            "bulk_replace",
            "bulk_merge",
        } and isinstance(result, (list, tuple)):
            return [
                out_model.model_validate(x).model_dump(
                    exclude_none=False, by_alias=True
                )
                for x in result
            ]
        # Single object case
        return out_model.model_validate(result).model_dump(
            exclude_none=False, by_alias=True
        )
    except Exception as e:
        # If serialization fails, let raw result through rather than failing the call
        logger.debug(
            "rpc output serialization failed for %s.%s: %s",
            model.__name__,
            alias,
            e,
            exc_info=True,
        )
        return _ensure_jsonable(result)


# ───────────────────────────────────────────────────────────────────────────────
# RPC wrapper builder
# ───────────────────────────────────────────────────────────────────────────────


def _build_rpc_callable(model: type, sp: OpSpec) -> Callable[..., Awaitable[Any]]:
    """
    Create an async callable that:
      1) validates payload (if schema present),
      2) runs the executor with the model's phase chains (Kernel-preferred),
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
        schemas_root = getattr(model, "schemas", None)
        alias_ns = getattr(schemas_root, alias, None)
        item_in_model = getattr(alias_ns, "in_item", None)

        raw_payload = _coerce_payload(payload)
        if target == "bulk_delete" and not isinstance(raw_payload, Mapping):
            raw_payload = {"ids": raw_payload}
        if (
            target.startswith("bulk_")
            and target != "bulk_delete"
            and isinstance(raw_payload, Sequence)
        ):
            merged_payload = []
            for item in raw_payload:
                if item_in_model and isinstance(item, Mapping):
                    norm = item_in_model.model_validate(dict(item)).model_dump(
                        exclude_none=True
                    )
                    merged_payload.append({**dict(item), **norm})
                elif item_in_model:
                    norm = item_in_model.model_validate(item).model_dump(
                        exclude_none=True
                    )
                    merged_payload.append(norm)
                else:
                    merged_payload.append(item)
        else:
            norm_payload = _validate_input(model, alias, target, raw_payload)
            merged_payload = dict(raw_payload)
            for key, value in norm_payload.items():
                merged_payload[key] = value

        # 2) build executor context & phases
        base_ctx: Dict[str, Any] = dict(ctx or {})
        base_ctx.setdefault("payload", merged_payload)
        base_ctx.setdefault("db", db)
        if request is not None:
            base_ctx.setdefault("request", request)
        # surface contextual metadata for runtime atoms
        app_ref = (
            getattr(request, "app", None)
            or base_ctx.get("app")
            or getattr(model, "api", None)
            or model
        )
        base_ctx.setdefault("app", app_ref)
        base_ctx.setdefault("api", base_ctx.get("api") or app_ref)
        base_ctx.setdefault("model", model)
        base_ctx.setdefault("op", alias)
        base_ctx.setdefault("method", alias)
        base_ctx.setdefault("target", target)
        # helpful env metadata
        base_ctx.setdefault(
            "env",
            SimpleNamespace(
                method=alias, params=merged_payload, target=target, model=model
            ),
        )

        phases = _get_phase_chains(model, alias)
        # RPC methods should return raw data for JSON-RPC envelopes;
        # remove response rendering atoms (which produce Starlette responses)
        # JSON-RPC endpoints handle rendering at the transport layer. Filter
        # out response rendering atoms but preserve any POST_RESPONSE hooks.
        phases["POST_RESPONSE"] = [
            fn
            for fn in phases.get("POST_RESPONSE", [])
            if not (
                isinstance(getattr(fn, "__tigrbl_label", None), str)
                and getattr(fn, "__tigrbl_label").endswith("@out:dump")
            )
        ]

        base_ctx["response_serializer"] = lambda r: _serialize_output(
            model, alias, target, r
        )
        # 3) run executor
        result = await _executor._invoke(
            request=request,
            db=db,
            phases=phases,
            ctx=base_ctx,
        )

        return result

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
