# tigrbl/v3/runtime/atoms/refresh/demand.py
from __future__ import annotations

from typing import Any, Iterable, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, _ensure_temp

# After the handler flushes changes; decide whether to hydrate DB-generated values.
ANCHOR = _ev.POST_FLUSH  # "post:flush"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    refresh:demand@post:flush

    Purpose
    -------
    Decide whether to hydrate refreshed values from the DB after a write (INSERT/UPDATE).
    We do NOT perform the refresh here; we only mark intent on the context so the
    executor (or handler) can perform the vendor-specific action (RETURNING/refresh()).

    Inputs (conventions)
    --------------------
    - ctx.persist : bool               → write op? (anchor is persist-tied but we guard)
    - ctx.temp["used_returning"] : bool              → a prior step already satisfied hydration
    - ctx.temp["hydrated_values"] : Mapping[str, Any]→ values captured from RETURNING
    - ctx.cfg.refresh_after_write : Optional[bool]   → policy override (true/false)
      (also checks ctx.cfg.refresh_policy.{always,never,auto})
    - ctx.bulk    : Optional[bool]    → bulk write; executor may choose a different strategy

    Effects
    -------
    - ctx.temp["refresh_demand"] : bool
    - ctx.temp["refresh_fields"] : tuple[str, ...] (hint: which fields likely changed in DB)
    - ctx.temp["refresh_reason"] : str (diagnostic only)
    """
    logger.debug("Running refresh:demand")
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping refresh:demand; ctx.persist is False")
        return

    temp = _ensure_temp(ctx)
    ov = opview_from_ctx(ctx)
    refresh_hints = tuple(ov.refresh_hints)

    # If RETURNING already produced hydrated values, skip unless policy forces refresh.
    returning_satisfied = bool(temp.get("used_returning")) or bool(
        temp.get("hydrated_values")
    )
    logger.debug("Returning satisfied: %s", returning_satisfied)

    # Policy: cfg.refresh_after_write wins if explicitly set; otherwise "auto".
    policy = _get_refresh_policy(ctx)
    logger.debug("Refresh policy: %s", policy)
    # auto → infer from specs (db-generated signals) OR absence of returning values
    needs_by_specs = bool(refresh_hints)
    logger.debug("Refresh hints: %s; fields=%s", needs_by_specs, refresh_hints)
    need_refresh = _decide(policy, returning_satisfied, needs_by_specs)
    logger.debug("Refresh decision: %s", need_refresh)

    temp["refresh_demand"] = bool(need_refresh)
    temp["refresh_fields"] = refresh_hints

    if need_refresh:
        temp["refresh_reason"] = _reason(
            policy, returning_satisfied, needs_by_specs, refresh_hints
        )
        logger.debug("Refresh scheduled: %s", temp["refresh_reason"])
    else:
        temp["refresh_reason"] = "skipped: returning_satisfied or policy=false"
        logger.debug("Refresh skipped: %s", temp["refresh_reason"])

    # Executor/handler will look at ctx.temp["refresh_demand"] and act accordingly.


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _get_refresh_policy(ctx: Any) -> str:
    """
    Return 'always' | 'never' | 'auto'.
    Accepts any of the following on ctx.cfg (first hit wins):
      - cfg.refresh_after_write: bool → True:'always' / False:'never'
      - cfg.refresh_policy: str in {'always','never','auto'}
    Defaults to 'auto'.
    """
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
    # auto
    if returning_satisfied:
        # RETURNING already hydrated values; only refresh if specs strongly indicate more work.
        return bool(needs_by_specs)
    # No returning: default to refresh to honor "hydrate after flush" decision.
    return True


def _reason(
    policy: str, returning_satisfied: bool, needs_by_specs: bool, fields: Iterable[str]
) -> str:
    parts = [f"policy={policy}"]
    parts.append(f"returning_satisfied={bool(returning_satisfied)}")
    parts.append(f"specs_need={bool(needs_by_specs)}")
    if fields:
        parts.append(f"fields={','.join(fields)}")
    return "; ".join(parts)


__all__ = ["ANCHOR", "run"]
