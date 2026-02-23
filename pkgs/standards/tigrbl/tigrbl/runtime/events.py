# tigrbl/v3/runtime/events.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Phases
#   - PRE_TX is a synthetic phase for security/dependency checks.
#   - START_TX / END_TX are reserved for system steps (no atom anchors there).
#   - Atoms bind only to the event anchors below.
# ──────────────────────────────────────────────────────────────────────────────

Phase = Literal[
    "PRE_TX",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "END_TX",
    "POST_RESPONSE",
]

PHASES: Tuple[Phase, ...] = (
    "PRE_TX",
    "START_TX",  # system-only
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "END_TX",  # system-only
    "POST_RESPONSE",
)

# ──────────────────────────────────────────────────────────────────────────────
# Canonical anchors (events) — the only moments atoms can bind to
# Keep these names stable; labels use them directly: step_kind:domain:subject@ANCHOR
# ──────────────────────────────────────────────────────────────────────────────

# PRE_HANDLER
SCHEMA_COLLECT_IN = "schema:collect_in"
IN_VALIDATE = "in:validate"

# HANDLER
RESOLVE_VALUES = "resolve:values"
PRE_FLUSH = "pre:flush"
EMIT_ALIASES_PRE = "emit:aliases:pre_flush"

# POST_HANDLER
POST_FLUSH = "post:flush"
EMIT_ALIASES_POST = "emit:aliases:post_refresh"
SCHEMA_COLLECT_OUT = "schema:collect_out"
OUT_BUILD = "out:build"

# POST_RESPONSE
EMIT_ALIASES_READ = "emit:aliases:readtime"
OUT_DUMP = "out:dump"

# Canonical order of event anchors within the request lifecycle.
# This ordering is global and stable; use it to produce deterministic plans/traces.
_EVENT_ORDER: Tuple[str, ...] = (
    # PRE_HANDLER
    SCHEMA_COLLECT_IN,
    IN_VALIDATE,
    # HANDLER
    RESOLVE_VALUES,
    PRE_FLUSH,
    EMIT_ALIASES_PRE,
    # POST_HANDLER
    POST_FLUSH,
    EMIT_ALIASES_POST,
    SCHEMA_COLLECT_OUT,
    OUT_BUILD,
    # POST_RESPONSE
    EMIT_ALIASES_READ,
    OUT_DUMP,
)


# Map each anchor to its phase and persistence tie.
# "persist_tied=True" means the anchor is pruned for non-persisting ops
# (e.g., read/list) and whenever an op is executed with persist=False.
@dataclass(frozen=True)
class AnchorInfo:
    name: str
    phase: Phase
    ordinal: int
    persist_tied: bool


_ANCHORS: Dict[str, AnchorInfo] = {
    # PRE_HANDLER (not persist-tied)
    SCHEMA_COLLECT_IN: AnchorInfo(SCHEMA_COLLECT_IN, "PRE_HANDLER", 0, False),
    IN_VALIDATE: AnchorInfo(IN_VALIDATE, "PRE_HANDLER", 1, False),
    RESOLVE_VALUES: AnchorInfo(RESOLVE_VALUES, "PRE_HANDLER", 2, True),
    PRE_FLUSH: AnchorInfo(PRE_FLUSH, "PRE_HANDLER", 3, True),
    EMIT_ALIASES_PRE: AnchorInfo(EMIT_ALIASES_PRE, "PRE_HANDLER", 4, True),
    # POST_HANDLER (mixed)
    POST_FLUSH: AnchorInfo(POST_FLUSH, "POST_HANDLER", 5, True),
    EMIT_ALIASES_POST: AnchorInfo(EMIT_ALIASES_POST, "POST_HANDLER", 6, True),
    SCHEMA_COLLECT_OUT: AnchorInfo(SCHEMA_COLLECT_OUT, "POST_HANDLER", 7, False),
    OUT_BUILD: AnchorInfo(OUT_BUILD, "POST_HANDLER", 8, False),
    # POST_RESPONSE (not persist-tied)
    EMIT_ALIASES_READ: AnchorInfo(EMIT_ALIASES_READ, "POST_RESPONSE", 9, False),
    OUT_DUMP: AnchorInfo(OUT_DUMP, "POST_RESPONSE", 10, False),
}

# ──────────────────────────────────────────────────────────────────────────────
# Public helpers
# ──────────────────────────────────────────────────────────────────────────────


def is_valid_event(anchor: str) -> bool:
    """True if the given anchor is one of the canonical events."""
    return anchor in _ANCHORS


def phase_for_event(anchor: str) -> Phase:
    """Return the Phase for a canonical event; raises on unknown anchors."""
    try:
        return _ANCHORS[anchor].phase
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def is_persist_tied(anchor: str) -> bool:
    """Return True if this event is pruned for non-persisting ops."""
    try:
        return _ANCHORS[anchor].persist_tied
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def get_anchor_info(anchor: str) -> AnchorInfo:
    """Return the full :class:`AnchorInfo` for a canonical event."""
    try:
        return _ANCHORS[anchor]
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def all_events_ordered() -> List[str]:
    """Return all canonical events in deterministic, lifecycle order."""
    return list(_EVENT_ORDER)


def events_for_phase(phase: Phase) -> List[str]:
    """Return the subset of events that belong to the given phase."""
    if phase not in PHASES:
        raise ValueError(f"Unknown phase: {phase!r}")
    return [a for a, info in _ANCHORS.items() if info.phase == phase]


def prune_events_for_persist(anchors: Iterable[str], *, persist: bool) -> List[str]:
    """
    Given a sequence of anchors, return a new list with persistence-tied events
    removed when persist=False. Unknown anchors raise ValueError.
    """
    out: List[str] = []
    for a in anchors:
        if not is_valid_event(a):
            raise ValueError(f"Unknown event anchor: {a!r}")
        if not persist and _ANCHORS[a].persist_tied:
            continue
        out.append(a)
    # keep canonical order irrespective of input order
    out.sort(key=lambda x: _ANCHORS[x].ordinal)
    return out


def order_events(anchors: Iterable[str]) -> List[str]:
    """
    Sort a set/list of anchors into canonical lifecycle order.
    Raises on unknown anchors.
    """
    anchors = list(anchors)
    for a in anchors:
        if a not in _ANCHORS:
            raise ValueError(f"Unknown event anchor: {a!r}")
    anchors.sort(key=lambda x: _ANCHORS[x].ordinal)
    return anchors


__all__ = [
    # Phases
    "Phase",
    "PHASES",
    # Anchors (constants)
    "SCHEMA_COLLECT_IN",
    "IN_VALIDATE",
    "RESOLVE_VALUES",
    "PRE_FLUSH",
    "EMIT_ALIASES_PRE",
    "POST_FLUSH",
    "EMIT_ALIASES_POST",
    "SCHEMA_COLLECT_OUT",
    "OUT_BUILD",
    "EMIT_ALIASES_READ",
    "OUT_DUMP",
    # Types / helpers
    "AnchorInfo",
    "is_valid_event",
    "phase_for_event",
    "is_persist_tied",
    "get_anchor_info",
    "all_events_ordered",
    "events_for_phase",
    "prune_events_for_persist",
    "order_events",
]
