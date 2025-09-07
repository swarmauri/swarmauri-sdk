from __future__ import annotations

import logging
from typing import Any, MutableMapping, Optional, Tuple

from ... import events as _ev
from ...kernel import _default_kernel as K

# After the handler flushes changes; decide whether to hydrate DB-generated values.
ANCHOR = _ev.POST_FLUSH  # "post:flush"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    refresh_hints = ov.refresh_hints

    temp = _ensure_temp(ctx)
    returning_satisfied = bool(temp.get("used_returning")) or bool(
        temp.get("hydrated_values")
    )

    policy = _get_refresh_policy(ctx)
    needs_by_specs = bool(refresh_hints)
    need_refresh = _decide(policy, returning_satisfied, needs_by_specs)

    temp["refresh_demand"] = bool(need_refresh)
    temp["refresh_fields"] = tuple(refresh_hints)

    if need_refresh:
        temp["refresh_reason"] = _reason(
            policy, returning_satisfied, needs_by_specs, refresh_hints
        )
    else:
        temp["refresh_reason"] = "skipped: returning_satisfied or policy=false"


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _get_refresh_policy(ctx: Any) -> str:
    cfg = getattr(ctx, "cfg", None)
    if cfg is not None:
        val = getattr(cfg, "refresh_after_write", None)
        if isinstance(val, bool):
            return "always" if val else "never"
        pol = getattr(getattr(cfg, "refresh_policy", None), "value", None) or getattr(
            cfg, "refresh_policy", None
        )
        if isinstance(pol, str) and pol in {"always", "never", "auto"}:
            return pol
    return "auto"


def _decide(policy: str, returning_satisfied: bool, needs_by_specs: bool) -> bool:
    if policy == "always":
        return True
    if policy == "never":
        return False
    if returning_satisfied:
        return bool(needs_by_specs)
    return True


def _reason(
    policy: str,
    returning_satisfied: bool,
    needs_by_specs: bool,
    fields: Tuple[str, ...],
) -> str:
    parts = [f"policy={policy}"]
    parts.append(f"returning_satisfied={bool(returning_satisfied)}")
    parts.append(f"specs_need={bool(needs_by_specs)}")
    if fields:
        parts.append(f"fields={','.join(fields)}")
    return "; ".join(parts)


__all__ = ["ANCHOR", "run"]
