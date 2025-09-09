# tigrbl/v3/runtime/labels.py
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Optional, Tuple, Literal, Iterable, Set
import re as _re

from . import events as _ev

# ──────────────────────────────────────────────────────────────────────────────
# Grammar
#   Canonical (display) form:
#     - secdep: <name>                      → "secdep:<name>"
#     - dep:    <name>                      → "dep:<name>"
#     - sys:    <subject>@<PHASE>           → "sys:txn:begin@START_TX"
#     - atom:   <domain>:<subject>@<anchor>[#field]
#     - hook:   <domain>:<subject>@<anchor>[#field]
#
#   Notes:
#   - step_kind ∈ {secdep, dep, sys, atom, hook}
#   - domains are restricted to: {emit, out, refresh, resolve, response, schema, storage, wire}
#   - anchors for atom/hook MUST be canonical events from runtime/events.py
#   - sys anchors MUST be one of PHASES (typically START_TX, HANDLER, END_TX)
# ──────────────────────────────────────────────────────────────────────────────

STEP_KINDS: Tuple[str, ...] = ("secdep", "dep", "sys", "atom", "hook")
StepKind = Literal["secdep", "dep", "sys", "atom", "hook"]
DOMAINS: Tuple[str, ...] = (
    "emit",
    "out",
    "refresh",
    "resolve",
    "response",
    "schema",
    "storage",
    "wire",
    "sys",
)

# minimal token rules (tight but readable)
# - domain/subject: letters, digits, underscore, dash; subject may contain colon to support composite subjects like "txn:begin"
# - field: letters, digits, underscore, dash, dot

_RE_NAME = _re.compile(r"^[A-Za-z0-9_.:-]+$")  # secdep/dep name (tolerant)
_RE_SUBJECT = _re.compile(
    r"^[A-Za-z0-9_:-]+$"
)  # allow ":" inside subject (e.g., "txn:begin")
_RE_FIELD = _re.compile(r"^[A-Za-z0-9_.-]+$")  # instance suffix


@dataclass(frozen=True)
class Label:
    kind: StepKind
    subject: str
    domain: Optional[str] = None
    anchor: Optional[str] = None
    field: Optional[str] = None

    # ── renderers ──────────────────────────────────────────────────────────────
    def render(self, *, pretty: bool = True) -> str:
        """
        Pretty = human-facing (short secdep/dep). False = always canonicalized shape when possible.
        """
        if self.kind in ("secdep", "dep"):
            return f"{self.kind}:{self.subject}"
        if self.kind == "sys":
            return f"sys:{self.subject}@{self.anchor}"
        # atom / hook
        base = f"{self.kind}:{self.domain}:{self.subject}@{self.anchor}"
        return f"{base}#{self.field}" if self.field else base

    __str__ = render

    # ── convenience ───────────────────────────────────────────────────────────
    def with_field(self, field: Optional[str]) -> "Label":
        _validate_field(field)
        return replace(self, field=field)

    def clear_field(self) -> "Label":
        return replace(self, field=None)

    # ── predicates ────────────────────────────────────────────────────────────
    @property
    def is_secdep(self) -> bool:
        return self.kind == "secdep"

    @property
    def is_dep(self) -> bool:
        return self.kind == "dep"

    @property
    def is_sys(self) -> bool:
        return self.kind == "sys"

    @property
    def is_atom(self) -> bool:
        return self.kind == "atom"

    @property
    def is_hook(self) -> bool:
        return self.kind == "hook"


# ──────────────────────────────────────────────────────────────────────────────
# Builders (typed helpers)
# ──────────────────────────────────────────────────────────────────────────────


def make_dep(name: str) -> Label:
    _require(_RE_NAME.match(name), f"Invalid dep name {name!r}")
    return Label(kind="dep", subject=name)


def make_secdep(name: str) -> Label:
    _require(_RE_NAME.match(name), f"Invalid secdep name {name!r}")
    return Label(kind="secdep", subject=name)


def make_sys(subject: str, phase: _ev.Phase) -> Label:
    _require(subject and _RE_SUBJECT.match(subject), f"Invalid sys subject {subject!r}")
    _require(phase in _ev.PHASES, f"Invalid sys phase {phase!r}")
    return Label(kind="sys", subject=subject, anchor=phase)


def make_atom(
    domain: str, subject: str, anchor: str, field: Optional[str] = None
) -> Label:
    _validate_domain(domain)
    _validate_subject(subject)
    _validate_anchor(anchor)
    _validate_field(field)
    return Label(
        kind="atom", domain=domain, subject=subject, anchor=anchor, field=field
    )


def make_hook(
    domain: str, subject: str, anchor: str, field: Optional[str] = None
) -> Label:
    _validate_domain(domain)
    _validate_subject(subject)
    _validate_anchor(anchor)
    _validate_field(field)
    return Label(
        kind="hook", domain=domain, subject=subject, anchor=anchor, field=field
    )


# ──────────────────────────────────────────────────────────────────────────────
# Parse / validate
# ──────────────────────────────────────────────────────────────────────────────


def parse(s: str) -> Label:
    """
    Parse a label string into a Label object. Raises ValueError on any mismatch.
    Accepts the canonical display forms described in the header.
    """
    if not isinstance(s, str) or ":" not in s:
        raise ValueError(f"Not a label: {s!r}")

    # secdep:name / dep:name
    if s.startswith("secdep:"):
        name = s[len("secdep:") :]
        _require(_RE_NAME.match(name), f"Invalid secdep name {name!r}")
        return Label(kind="secdep", subject=name)
    if s.startswith("dep:"):
        name = s[len("dep:") :]
        _require(_RE_NAME.match(name), f"Invalid dep name {name!r}")
        return Label(kind="dep", subject=name)

    # sys:subject@PHASE
    if s.startswith("sys:"):
        rest = s[len("sys:") :]
        try:
            subject, phase = rest.split("@", 1)
        except ValueError as e:
            raise ValueError("System label must be 'sys:<subject>@<PHASE>'") from e
        _require(_RE_SUBJECT.match(subject), f"Invalid sys subject {subject!r}")
        _require(phase in _ev.PHASES, f"Invalid sys phase {phase!r}")
        return Label(kind="sys", subject=subject, anchor=phase)

    # atom:/hook:
    if s.startswith("atom:") or s.startswith("hook:"):
        kind: StepKind = "atom" if s.startswith("atom:") else "hook"
        rest = s[len("atom:") :] if kind == "atom" else s[len("hook:") :]

        # Split domain:subject@anchor[#field]
        try:
            dom, rest2 = rest.split(":", 1)
        except ValueError as e:
            raise ValueError(f"{kind} label must start with '<domain>:...'") from e

        try:
            subj, rest3 = rest2.split("@", 1)
        except ValueError as e:
            raise ValueError(f"{kind} label must include '@<anchor>'") from e

        anchor, field = _split_anchor_field(rest3)

        _validate_domain(dom)

        _validate_subject(subj)
        _validate_anchor(anchor)
        _validate_field(field)

        return Label(kind=kind, domain=dom, subject=subj, anchor=anchor, field=field)

    raise ValueError(f"Unknown step kind in label {s!r}")


def validate(label: Label) -> None:
    """Raise ValueError if the label violates the grammar or constraints."""
    k = label.kind
    if k in ("secdep", "dep"):
        _require(
            label.subject and _RE_NAME.match(label.subject),
            f"Invalid {k} name {label.subject!r}",
        )
        _require(
            label.domain is None and label.anchor is None,
            f"{k} cannot carry domain/anchor",
        )
        _validate_field(label.field)
        return

    if k == "sys":
        _require(
            label.subject and _RE_SUBJECT.match(label.subject),
            f"Invalid sys subject {label.subject!r}",
        )
        _require(label.anchor in _ev.PHASES, f"Invalid sys phase {label.anchor!r}")
        _require(label.domain is None, "sys cannot carry a domain")
        _validate_field(label.field)
        return

    if k == "atom":
        _validate_domain(label.domain)
        _validate_subject(label.subject)
        _validate_anchor(label.anchor)
        _validate_field(label.field)
        return

    if k == "hook":
        _validate_domain(label.domain)
        _validate_subject(label.subject)
        _validate_anchor(label.anchor)
        _validate_field(label.field)
        return

    raise ValueError(f"Unknown label kind {k!r}")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers / Legend
# ──────────────────────────────────────────────────────────────────────────────


def _split_anchor_field(s: str) -> Tuple[str, Optional[str]]:
    """Split 'anchor[#field]' into (anchor, field?)."""
    if "#" in s:
        anchor, field = s.split("#", 1)
        return anchor, (field or None)
    return s, None


def _validate_domain(domain: Optional[str]) -> None:
    _require(
        domain is not None and domain in DOMAINS,
        f"Invalid domain {domain!r}; expected one of {list(DOMAINS)}",
    )


def _validate_subject(subj: Optional[str]) -> None:
    _require(subj is not None and _RE_SUBJECT.match(subj), f"Invalid subject {subj!r}")


def _validate_anchor(anchor: Optional[str]) -> None:
    _require(
        anchor is not None and (_ev.is_valid_event(anchor) or anchor in _ev.PHASES),
        f"Invalid or unknown anchor {anchor!r}",
    )


def _validate_field(field: Optional[str]) -> None:
    if field is None:
        return
    _require(_RE_FIELD.match(field), f"Invalid field instance suffix {field!r}")


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def legend() -> Dict[str, object]:
    """
    Return a stable dictionary suitable for a /diagnostics/labels/legend endpoint.
    Includes step kinds, atom domains, sys phases, and ordered anchors.
    """
    return {
        "step_kinds": STEP_KINDS,
        "atom_domains": DOMAINS,
        "sys_phases": _ev.PHASES,
        "anchors": _ev.all_events_ordered(),
        "notes": {
            "secdep/dep": "Run before any anchor; shape is 'secdep:<name>' / 'dep:<name>'.",
            "sys": "Subject describes the system op; anchor is a PHASE.",
            "atom/hook": "Use '<domain>:<subject>@<anchor>#field' (field optional).",
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Bulk utilities (nice-to-haves for planner/trace)
# ──────────────────────────────────────────────────────────────────────────────


def ensure_all_valid(labels: Iterable[Label]) -> None:
    for lbl in labels:
        validate(lbl)


def only_atoms(labels: Iterable[Label]) -> Tuple[Label, ...]:
    return tuple(label for label in labels if label.kind == "atom")


def only_hooks(labels: Iterable[Label]) -> Tuple[Label, ...]:
    return tuple(label for label in labels if label.kind == "hook")


def fields_used(labels: Iterable[Label]) -> Set[str]:
    return {label.field for label in labels if label.field}


__all__ = [
    "STEP_KINDS",
    "StepKind",
    "DOMAINS",
    "Label",
    "make_dep",
    "make_secdep",
    "make_sys",
    "make_atom",
    "make_hook",
    "parse",
    "validate",
    "legend",
    "ensure_all_valid",
    "only_atoms",
    "only_hooks",
    "fields_used",
]
