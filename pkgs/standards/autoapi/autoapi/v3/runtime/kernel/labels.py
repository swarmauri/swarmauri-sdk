from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence

from .. import events as _ev
from ...op.types import StepFn

_AtomRun = Callable[[Optional[object], Any], Any]


def _infer_domain_subject(run: _AtomRun) -> tuple[str | None, str | None]:
    mod = getattr(run, "__module__", "") or ""
    parts = mod.split(".")
    try:
        i = parts.index("atoms")
        domain = parts[i + 1] if i + 1 < len(parts) else None
        subject = parts[i + 2] if i + 2 < len(parts) else None
        return domain, subject
    except ValueError:
        return None, None


def _make_label(anchor: str, run: _AtomRun) -> str | None:
    d, s = _infer_domain_subject(run)
    if not (d and s):
        return None
    return f"atom:{d}:{s}@{anchor}"


def _labels_from_chains(chains: Mapping[str, Sequence[StepFn]]) -> list[str]:
    ordered_events = _ev.all_events_ordered()
    labels: list[str] = []
    phase_for = {a: _ev.get_anchor_info(a).phase for a in ordered_events}
    for anchor in ordered_events:
        phase = phase_for[anchor]
        for step in chains.get(phase, []) or []:
            lbl = getattr(step, "__autoapi_label", None)
            if isinstance(lbl, str) and lbl.endswith(f"@{anchor}"):
                labels.append(lbl)
    return labels


__all__ = ["_make_label", "_labels_from_chains"]
