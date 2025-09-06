# autoapi/v3/runtime/atoms/refresh/demand.py
from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple
import logging

from ... import events as _ev

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
    - ctx.specs   : {field -> ColumnSpec}
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
        return

    temp = _ensure_temp(ctx)
    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}

    # If RETURNING already produced hydrated values, skip unless policy forces refresh.
    returning_satisfied = bool(temp.get("used_returning")) or bool(
        temp.get("hydrated_values")
    )

    # Policy: cfg.refresh_after_write wins if explicitly set; otherwise "auto".
    policy = _get_refresh_policy(ctx)
    # auto → infer from specs (db-generated signals) OR absence of returning values
    needs_by_specs, fields = _scan_specs_for_refresh(specs)
    need_refresh = _decide(policy, returning_satisfied, needs_by_specs)

    temp["refresh_demand"] = bool(need_refresh)
    temp["refresh_fields"] = tuple(fields)

    if need_refresh:
        temp["refresh_reason"] = _reason(
            policy, returning_satisfied, needs_by_specs, fields
        )
    else:
        temp["refresh_reason"] = "skipped: returning_satisfied or policy=false"

    # Executor/handler will look at ctx.temp["refresh_demand"] and act accordingly.


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


def _scan_specs_for_refresh(specs: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    """
    Heuristically determine if any column is likely DB-generated and requires hydration.
    We examine StorageSpec-like attributes but keep this tolerant (no hard dependency).
    """
    need = False
    fields: list[str] = []

    for fname, col in specs.items():
        s = getattr(col, "storage", None)
        if s is None:
            continue

        # Common server-side generation signals
        flags = (
            getattr(s, "server_default", None),
            getattr(s, "server_onupdate", None),
            getattr(s, "computed", None),
            getattr(s, "sa_computed", None),
            getattr(s, "db_generated", None),
            getattr(s, "identity", None),
            getattr(s, "sequence", None),
            getattr(s, "autoincrement", None),
            getattr(s, "onupdate", None),
        )
        pk = bool(getattr(s, "primary_key", False))
        # Consider PKs with autoincrement/identity as refresh candidates
        if any(bool(f) for f in flags) or (
            pk and bool(getattr(s, "autoincrement", False))
        ):
            need = True
            fields.append(fname)

    return need, tuple(sorted(set(fields)))


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
