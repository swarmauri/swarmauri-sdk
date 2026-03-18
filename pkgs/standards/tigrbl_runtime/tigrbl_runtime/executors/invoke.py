# tigrbl/runtime/executor/invoke.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Mapping, MutableMapping, Optional, Union

from .types import _Ctx, PhaseChains, Request, Session, AsyncSession
from tigrbl_kernel.helpers import _run_chain, _g
from tigrbl_atoms.atoms.sys._db import _in_transaction
from ..runtime.status import create_standardized_error, to_rpc_error_payload
from ..config.constants import CTX_SKIP_PERSIST_FLAG
from tigrbl_ops_oltp.crud import ops as _crud_ops
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value, _single_pk_name

logger = logging.getLogger(__name__)

_OPVIEW_CACHE_ATTR = "__tigrbl_cached_opviews__"
_OPSPEC_BY_ALIAS_CACHE_ATTR = "__tigrbl_cached_opspec_by_alias__"
_LOG_NOISE_REDUCED = False
_NOISY_TIGRBL_LOGGERS = (
    "tigrbl_ops_oltp.crud.helpers.model",
    "tigrbl_core._spec.column_spec",
)


def _reduce_log_noise() -> None:
    global _LOG_NOISE_REDUCED
    if _LOG_NOISE_REDUCED:
        return
    _LOG_NOISE_REDUCED = True
    for logger_name in _NOISY_TIGRBL_LOGGERS:
        target_logger = logging.getLogger(logger_name)
        if target_logger.getEffectiveLevel() <= logging.INFO:
            target_logger.setLevel(logging.WARNING)


def _default_status_for_alias(alias: Any, target: Any = None) -> int:
    verb = target if isinstance(target, str) and target else alias
    return 201 if verb in {"create", "bulk_create"} else 200


def _normalize_result_payload(payload: Any) -> Any:
    if (
        isinstance(payload, (str, int, float, bool, bytes, bytearray))
        or payload is None
    ):
        return payload
    if hasattr(payload, "status_code") and hasattr(payload, "body"):
        return payload
    if isinstance(payload, Mapping):
        return {str(k): _normalize_result_payload(v) for k, v in payload.items()}
    if isinstance(payload, (list, tuple, set)):
        return [_normalize_result_payload(v) for v in payload]

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        try:
            return _normalize_result_payload(model_dump())
        except Exception:
            pass

    obj_dict = getattr(payload, "__dict__", None)
    if isinstance(obj_dict, dict):
        data = {
            k: v
            for k, v in obj_dict.items()
            if not k.startswith("_") and not callable(v)
        }
        if data:
            return _normalize_result_payload(data)

    return str(payload)


def _unwrap_ctx_result(value: Any) -> Any:
    """Return user-facing payload when runtime atoms return context objects."""
    current = value
    for _ in range(8):
        if current is None or isinstance(
            current, (str, int, float, bool, Mapping, list, tuple, set)
        ):
            return current

        direct = getattr(current, "result", None)
        if direct is not None and direct is not current:
            current = direct
            continue

        payload = getattr(current, "response_payload", None)
        if payload is not None and payload is not current:
            current = payload
            continue

        response = getattr(current, "response", None)
        if response is not None:
            response_result = getattr(response, "result", None)
            if response_result is not None and response_result is not current:
                current = response_result
                continue

        bag = getattr(current, "bag", None)
        if isinstance(bag, Mapping) and bag.get("result") is not None:
            nested = bag.get("result")
            if nested is not current:
                current = nested
                continue

        return current

    return current


def _resolve_op_spec(model: type, alias: str) -> Any:
    cached_by_alias = getattr(model, _OPSPEC_BY_ALIAS_CACHE_ATTR, None)
    if not isinstance(cached_by_alias, dict):
        cached_by_alias = {
            str(getattr(spec, "alias", "")): spec
            for spec in (getattr(getattr(model, "ops", None), "all", ()) or ())
            if getattr(spec, "alias", None)
        }
        setattr(model, _OPSPEC_BY_ALIAS_CACHE_ATTR, cached_by_alias)
    return cached_by_alias.get(alias)


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _crud_result_fallback(ctx: _Ctx, current_result: Any) -> Any:
    alias = str(ctx.get("op") or "").lower()
    if alias not in {"read", "update", "replace"}:
        return current_result

    model = ctx.get("model")
    db = ctx.get("db")
    if not isinstance(model, type) or db is None:
        return current_result

    try:
        pk_name = _single_pk_name(model)
    except Exception:
        return current_result

    payload = ctx.get("payload")
    path_params = ctx.get("path_params")
    ident = None
    if isinstance(path_params, Mapping) and pk_name in path_params:
        ident = path_params.get(pk_name)
    elif isinstance(payload, Mapping) and pk_name in payload:
        ident = payload.get(pk_name)
    if ident is None:
        return current_result

    ident = _coerce_pk_value(model, ident)

    if alias == "read":
        needs_fallback = current_result is None
        if isinstance(current_result, Mapping):
            if pk_name not in current_result:
                needs_fallback = True
            else:
                data_keys = [k for k in current_result.keys() if k != pk_name]
                if data_keys and all(current_result.get(k) is None for k in data_keys):
                    needs_fallback = True
        if not needs_fallback:
            return current_result
        return await _crud_ops.read(model, ident, db)

    if current_result is None and isinstance(payload, Mapping):
        if alias == "update":
            return await _crud_ops.update(model, ident, dict(payload), db)
        return await _crud_ops.replace(model, ident, dict(payload), db)

    return current_result


async def _rollback_if_owned(
    db: Union[Session, AsyncSession, None],
    owns_tx: bool,
    *,
    phases: Optional[PhaseChains],
    ctx: Any,
) -> None:
    if not owns_tx or db is None:
        return
    if not _g(phases, "ON_ROLLBACK"):
        try:
            await _maybe_await(db.rollback())
        except Exception:  # pragma: no cover
            logger.exception("Rollback failed", exc_info=True)
    try:
        await _run_chain(ctx, _g(phases, "ON_ROLLBACK"), phase="ON_ROLLBACK")
    except Exception:  # pragma: no cover
        pass


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession, None],
    phases: Optional[PhaseChains],
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Execute an operation through explicit phases with strict write policies."""

    _reduce_log_noise()

    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    if getattr(ctx, "app", None) is None and getattr(ctx, "router", None) is not None:
        ctx.app = ctx.router
    if getattr(ctx, "op", None) is None and getattr(ctx, "method", None) is not None:
        ctx.op = ctx.method
    env = ctx.get("env")
    op_name = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if env is None:
        ctx["env"] = SimpleNamespace(method=op_name)
    elif getattr(env, "method", None) in (None, "", "unknown"):
        try:
            setattr(env, "method", op_name)
        except Exception:
            ctx["env"] = SimpleNamespace(method=op_name)
    if getattr(ctx, "model", None) is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            ctx.model = type(obj)
    if getattr(ctx, "opview", None) is None:
        model = getattr(ctx, "model", None)
        alias = getattr(ctx, "op", None)
        specs = ctx.get("specs")
        if (
            isinstance(model, type)
            and isinstance(alias, str)
            and isinstance(specs, Mapping)
        ):
            try:
                cached_views = getattr(model, _OPVIEW_CACHE_ATTR, None)
                if not isinstance(cached_views, dict):
                    cached_views = {}
                    setattr(model, _OPVIEW_CACHE_ATTR, cached_views)

                cached_view = cached_views.get(alias)
                if cached_view is not None:
                    ctx.opview = cached_view
                else:
                    from tigrbl_kernel.opview_compiler import compile_opview_from_specs

                    op_spec = _resolve_op_spec(model, alias)
                    if op_spec is None:
                        op_spec = SimpleNamespace(alias=alias)
                    compiled_view = compile_opview_from_specs(specs, op_spec)
                    cached_views[alias] = compiled_view
                    ctx.opview = compiled_view
            except Exception:
                pass
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))
    skip_egress: bool = bool(ctx.get("skip_egress"))
    if not callable(ctx.get("rpc_error_builder")):
        ctx["rpc_error_builder"] = lambda exc: to_rpc_error_payload(
            create_standardized_error(exc)
        )

    existed_tx_before = _in_transaction(db) if db is not None else False

    async def _run_phase(
        name: str,
        *,
        allow_flush: bool,
        allow_commit: bool,
        in_tx: bool,
        require_owned_for_commit: bool = True,
        nonfatal: bool = False,
        owns_tx_for_phase: Optional[bool] = None,
    ) -> None:
        chain = _g(phases, name)
        if not chain:
            return

        owns_tx_now = bool(owns_tx_for_phase)
        if owns_tx_for_phase is None:
            owns_tx_now = not existed_tx_before

        del allow_flush, allow_commit, require_owned_for_commit
        ctx.phase = name
        ctx.owns_tx = owns_tx_now

        try:
            await _run_chain(ctx, chain, phase=name)
        except Exception as exc:
            ctx.error = exc
            if in_tx:
                await _rollback_if_owned(db, owns_tx_now, phases=phases, ctx=ctx)
            err_name = f"ON_{name}_ERROR"
            try:
                await _run_chain(
                    ctx, _g(phases, err_name) or _g(phases, "ON_ERROR"), phase=err_name
                )
            except Exception:  # pragma: no cover
                pass
            if nonfatal:
                logger.exception("%s failed (nonfatal): %s", name, exc)
                return
            raise create_standardized_error(exc)

    await _run_phase(
        "INGRESS_BEGIN", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase(
        "INGRESS_PARSE", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase(
        "INGRESS_ROUTE", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase("PRE_TX_BEGIN", allow_flush=False, allow_commit=False, in_tx=False)

    if not skip_persist:
        await _run_phase(
            "START_TX",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            require_owned_for_commit=False,
        )

    await _run_phase(
        "PRE_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "POST_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "PRE_COMMIT", allow_flush=False, allow_commit=False, in_tx=not skip_persist
    )

    if not skip_persist:
        # If this invocation started outside a transaction, the runtime owns the
        # commit decision even when the backend uses implicit/autobegin semantics.
        owns_tx_for_commit = not existed_tx_before
        await _run_phase(
            "END_TX",
            allow_flush=True,
            allow_commit=True,
            in_tx=True,
            require_owned_for_commit=False,
            owns_tx_for_phase=owns_tx_for_commit,
        )

    from types import SimpleNamespace as _NS

    if ctx.get("result") is None:
        fallback = (
            ctx.get("obj")
            or ctx.get("objs")
            or (
                ctx.get("temp", {}).get("egress", {}).get("result")
                if isinstance(ctx.get("temp"), Mapping)
                else None
            )
        )
        if fallback is not None:
            ctx["result"] = fallback

    serializer = ctx.get("response_serializer")
    current_result = ctx.get("result")
    temp = ctx.get("temp") if isinstance(ctx, Mapping) else None
    rpc_error = temp.get("rpc_error") if isinstance(temp, Mapping) else None
    response_state = getattr(ctx, "response", None)
    if current_result is None and response_state is not None:
        current_result = getattr(response_state, "result", None)
    if current_result is None:
        current_result = getattr(ctx, "obj", None)

    current_result = _unwrap_ctx_result(current_result)
    current_result = await _crud_result_fallback(ctx, current_result)

    if isinstance(rpc_error, Mapping):
        ctx["result"] = None
    elif callable(serializer):
        try:
            ctx["result"] = serializer(current_result)
        except Exception:
            logger.exception("response serialization failed", exc_info=True)
    else:
        ctx["result"] = _normalize_result_payload(current_result)

    if getattr(ctx, "status_code", None) is None:
        ctx.status_code = _default_status_for_alias(
            getattr(ctx, "op", None), getattr(ctx, "target", None)
        )

    response_obj = getattr(ctx, "response", None)
    if response_obj is None:
        ctx.response = _NS(result=ctx.get("result"))
    else:
        setattr(response_obj, "result", ctx.get("result"))

    pre_egress_result = ctx.get("result")

    await _run_phase("POST_COMMIT", allow_flush=True, allow_commit=False, in_tx=False)

    if not skip_egress:
        await _run_phase(
            "POST_RESPONSE",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            nonfatal=True,
        )

        await _run_phase(
            "EGRESS_SHAPE", allow_flush=False, allow_commit=False, in_tx=False
        )
        await _run_phase(
            "EGRESS_FINALIZE", allow_flush=False, allow_commit=False, in_tx=False
        )
    if ctx.get("result") is not None and getattr(ctx, "response", None) is not None:
        setattr(ctx.response, "result", ctx.get("result"))

    release = None
    if isinstance(temp, Mapping):
        release = temp.pop("__sys_db_release__", None)
    if callable(release):
        release()

    if skip_egress:
        result = _unwrap_ctx_result(pre_egress_result)
        result = _normalize_result_payload(result)
        if result is not None:
            ctx["result"] = result
            if getattr(ctx, "response", None) is not None:
                setattr(ctx.response, "result", result)
        return result

    if getattr(ctx, "response", None) is not None:
        result = getattr(ctx.response, "result", ctx.get("result"))
        result = _unwrap_ctx_result(result)
        if isinstance(result, Mapping) and {"status_code", "headers", "body"}.issubset(
            result
        ):
            body = result.get("body")
            if body is None and pre_egress_result is not None:
                result = pre_egress_result
        if result is not None:
            ctx["result"] = result
            setattr(ctx.response, "result", result)
        return result

    result = _unwrap_ctx_result(ctx.get("result"))
    if isinstance(result, Mapping) and {"status_code", "headers", "body"}.issubset(
        result
    ):
        body = result.get("body")
        if body is None and pre_egress_result is not None:
            result = pre_egress_result
    if result is not None:
        ctx["result"] = result
    return result


__all__ = ["_invoke"]
