# tigrbl/runtime/executor/invoke.py
from __future__ import annotations

import logging
from typing import Any, Mapping, MutableMapping, Optional, Union

from .types import _Ctx, PhaseChains, Request, Session, AsyncSession
from .helpers import _in_tx, _run_chain, _g
from tigrbl_kernel.guards import _install_db_guards, _rollback_if_owned
from ..status import create_standardized_error
from ...config.constants import CTX_SKIP_PERSIST_FLAG

logger = logging.getLogger(__name__)


def _default_status_for_alias(alias: Any) -> int:
    return 201 if alias in {"create", "bulk_create"} else 200


def _normalize_result_payload(payload: Any) -> Any:
    if isinstance(payload, (str, int, float, bool)) or payload is None:
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


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession, None],
    phases: Optional[PhaseChains],
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Execute an operation through explicit phases with strict write policies."""

    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    if getattr(ctx, "app", None) is None and getattr(ctx, "router", None) is not None:
        ctx.app = ctx.router
    if getattr(ctx, "op", None) is None and getattr(ctx, "method", None) is not None:
        ctx.op = ctx.method
    if getattr(ctx, "model", None) is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            ctx.model = type(obj)
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))

    existed_tx_before = _in_tx(db) if db is not None else False

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

        eff_allow_flush = allow_flush and (not skip_persist)
        eff_allow_commit = allow_commit and (not skip_persist)

        owns_tx_now = bool(owns_tx_for_phase)
        if owns_tx_for_phase is None:
            owns_tx_now = not existed_tx_before

        guard = _install_db_guards(
            db,
            phase=name,
            allow_flush=eff_allow_flush,
            allow_commit=eff_allow_commit,
            require_owned_tx_for_commit=require_owned_for_commit,
            owns_tx=owns_tx_now,
        )

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
        finally:
            guard.restore()

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
        ctx.status_code = _default_status_for_alias(getattr(ctx, "op", None))

    response_obj = getattr(ctx, "response", None)
    if response_obj is None:
        ctx.response = _NS(result=ctx.get("result"))
    else:
        setattr(response_obj, "result", ctx.get("result"))

    await _run_phase("POST_COMMIT", allow_flush=True, allow_commit=False, in_tx=False)

    await _run_phase(
        "POST_RESPONSE",
        allow_flush=False,
        allow_commit=False,
        in_tx=False,
        nonfatal=True,
    )

    await _run_phase("EGRESS_SHAPE", allow_flush=False, allow_commit=False, in_tx=False)
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

    if getattr(ctx, "response", None) is not None:
        return getattr(ctx.response, "result", ctx.get("result"))
    return ctx.get("result")


__all__ = ["_invoke"]
