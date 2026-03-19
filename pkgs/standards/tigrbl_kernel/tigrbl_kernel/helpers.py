from __future__ import annotations

import inspect
import logging
from typing import Any, Iterable, Mapping, Optional, Sequence

try:
    from tigrbl_kernel import trace as _trace  # type: ignore
except Exception:  # pragma: no cover
    _trace = None  # type: ignore

logger = logging.getLogger(__name__)


def _normalize_payload(payload: Any) -> Any:
    if isinstance(payload, (str, int, float, bool)) or payload is None:
        return payload
    if isinstance(payload, dict):
        return {str(k): _normalize_payload(v) for k, v in payload.items()}
    if isinstance(payload, (list, tuple, set)):
        return [_normalize_payload(v) for v in payload]

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        try:
            return _normalize_payload(model_dump())
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
            return _normalize_payload(data)

    return str(payload)


async def _maybe_await(v: Any) -> Any:
    if inspect.isawaitable(v):
        return await v  # type: ignore[func-returns-value]
    return v


def _trace_ready(ctx: Any) -> bool:
    if _trace is None:
        return False
    temp = getattr(ctx, "temp", None)
    return isinstance(temp, dict) and "__trace__" in temp


async def _run_chain(ctx: Any, chain: Optional[Iterable[Any]], *, phase: str) -> None:
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict) and temp.get("rpc_short_circuit"):
        if phase not in {"EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}:
            return

    if not chain:
        return

    isawaitable = inspect.isawaitable
    trace_active = _trace_ready(ctx)

    for idx, step in enumerate(chain):
        label = getattr(step, "__tigrbl_label", None)
        if not isinstance(label, str) or not label:
            label = f"phase:{phase}:step:{idx}"

        seq = _trace.start(ctx, label) if trace_active else None
        before_post_response = None
        if phase == "POST_RESPONSE":
            response = getattr(ctx, "response", None)
            before_value = getattr(response, "result", None)
            if before_value is None:
                before_value = ctx.get("result")
            before_post_response = _normalize_payload(before_value)

        try:
            rv = step(ctx)
            if isawaitable(rv):
                rv = await rv  # type: ignore[func-returns-value]
            if rv is not None and rv is not ctx:
                ctx.result = rv
            if trace_active:
                _trace.end(ctx, seq, status=_trace.OK)

            if (
                phase == "POST_RESPONSE"
                and getattr(step, "__tigrbl_label", None) is None
            ):
                temp_ns = getattr(ctx, "temp", None)
                if not isinstance(temp_ns, dict):
                    continue

                egress = temp_ns.get("egress")
                if not isinstance(egress, dict):
                    continue

                response = getattr(ctx, "response", None)
                result = getattr(response, "result", None)
                if result is None:
                    result = ctx.get("result")
                else:
                    ctx.result = result

                if result is None:
                    continue
                if hasattr(result, "status_code") and hasattr(result, "body"):
                    continue
                if isinstance(result, dict) and any(
                    key in result for key in ("status_code", "headers", "body")
                ):
                    continue

                safe_result = _normalize_payload(result)
                if safe_result == before_post_response:
                    continue

                egress["wire_payload"] = safe_result
                enveloped = egress.get("enveloped")
                if isinstance(enveloped, dict) and "result" in enveloped:
                    enveloped["result"] = safe_result
                elif enveloped is not None and not isinstance(enveloped, dict):
                    egress["enveloped"] = safe_result

                transport_response = egress.get("transport_response")
                if isinstance(transport_response, dict):
                    transport_response["body"] = egress.get("enveloped", safe_result)
        except Exception as exc:
            temp = getattr(ctx, "temp", None)
            route = temp.get("route") if isinstance(temp, dict) else None
            rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
            if isinstance(rpc_env, Mapping):
                ctx.status_code = 200
                ctx.result = None
                if isinstance(temp, dict):
                    temp["rpc_short_circuit"] = True
                    if not isinstance(temp.get("rpc_error"), dict):
                        builder = ctx.get("rpc_error_builder")
                        if callable(builder):
                            try:
                                temp["rpc_error"] = builder(exc)
                            except Exception:
                                temp["rpc_error"] = {"message": str(exc)}
                        else:
                            temp["rpc_error"] = {"message": str(exc)}
                if trace_active:
                    _trace.attach_error(ctx, seq, exc)
                    _trace.end(ctx, seq, status=_trace.ERROR)
                return
            if trace_active:
                _trace.attach_error(ctx, seq, exc)
                _trace.end(ctx, seq, status=_trace.ERROR)
            raise


def _g(phases: Optional[Mapping[str, Sequence[Any]]], key: str) -> Sequence[Any]:
    return () if not phases else phases.get(key, ())


__all__ = ["_maybe_await", "_run_chain", "_g"]
