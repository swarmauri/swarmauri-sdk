# autoapi/v3/runtime/ordering.py
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import events as _ev
from .labels import Label

# ──────────────────────────────────────────────────────────────────────────────
# Default in-anchor preferences (safe, minimal)
#   - Each entry is a list of "domain:subject" tokens in desired order.
#   - DEFAULT_EDGES are derived from these (u -> v).
# ──────────────────────────────────────────────────────────────────────────────

# tokens: "domain:subject"
_PREF: Dict[str, Tuple[str, ...]] = {
    _ev.SCHEMA_COLLECT_IN:  ("schema:collect_in",),
    _ev.IN_VALIDATE:        ("wire:build_in", "wire:validate_in"),
    _ev.RESOLVE_VALUES:     ("resolve:assemble", "resolve:paired_gen"),
    _ev.PRE_FLUSH:          ("storage:to_stored",),
    _ev.EMIT_ALIASES_PRE:   ("emit:paired_pre",),
    _ev.POST_FLUSH:         ("refresh:demand",),
    _ev.EMIT_ALIASES_POST:  ("emit:paired_post",),
    _ev.SCHEMA_COLLECT_OUT: ("schema:collect_out",),
    _ev.OUT_BUILD:          ("wire:build_out",),
    _ev.EMIT_ALIASES_READ:  ("emit:readtime_alias",),
    _ev.OUT_DUMP:           ("wire:dump", "out:masking"),
}

def _derive_edges(pref: Mapping[str, Sequence[str]]) -> Dict[str, Tuple[Tuple[str, str], ...]]:
    out: Dict[str, Tuple[Tuple[str, str], ...]] = {}
    for anchor, seq in pref.items():
        edges: List[Tuple[str, str]] = []
        for i in range(len(seq) - 1):
            edges.append((seq[i], seq[i + 1]))
        out[anchor] = tuple(edges)
    return out

_DEFAULT_EDGES: Dict[str, Tuple[Tuple[str, str], ...]] = _derive_edges(_PREF)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AnchorPolicy:
    """
    Extra ordering rules for a specific anchor.
    - edges: (u, v) means "u before v" where u/v are "domain:subject" tokens.
    - prefer: stable tie-break priority list of tokens.
    """
    edges: Tuple[Tuple[str, str], ...] = ()
    prefer: Tuple[str, ...] = ()


def flatten(
    labels: Iterable[Label],
    *,
    persist: bool,
    anchor_policies: Optional[Mapping[str, AnchorPolicy]] = None,
) -> List[Label]:
    """
    Produce a full, flattened order of labels across all phases.

    Rules:
    - secdep → dep → PRE_HANDLER anchors → START_TX sys → HANDLER anchors →
      HANDLER sys → POST_HANDLER anchors → END_TX sys → POST_RESPONSE anchors
    - sys labels are pruned when persist=False (no txn for read-only ops).
    - persist-tied anchors are pruned when persist=False (see events.is_persist_tied).
    - Within each anchor, perform a topo sort using DEFAULT_EDGES + anchor_policies[anchor].edges,
      with stable tie-breaks using preferences + (kind, domain, subject, field).
    """
    # Partition by kind/phase/anchor
    secdeps: List[Label] = []
    deps: List[Label] = []
    sys_by_phase: Dict[_ev.Phase, List[Label]] = defaultdict(list)
    by_anchor: Dict[str, List[Label]] = defaultdict(list)

    for lbl in labels:
        if lbl.kind == "secdep":
            secdeps.append(lbl)
        elif lbl.kind == "dep":
            deps.append(lbl)
        elif lbl.kind == "sys":
            # accept any phase, but common are START_TX/HANDLER/END_TX
            phase = lbl.anchor  # type: ignore[assignment]
            if phase not in _ev.PHASES:
                raise ValueError(f"System label carries unknown phase: {lbl}")
            sys_by_phase[phase].append(lbl)
        else:
            # atom/hook (must carry anchor)
            if not lbl.anchor:
                raise ValueError(f"Label missing anchor: {lbl}")
            by_anchor[lbl.anchor].append(lbl)

    # Deterministic order for secdep/dep blocks
    secdeps.sort(key=lambda l: (l.subject,))
    deps.sort(key=lambda l: (l.subject,))

    # Anchor list honoring persist pruning + canonical order
    anchors_present = tuple(a for a in by_anchor.keys())
    anchors = _ev.order_events(anchors_present)
    if not persist:
        anchors = _ev.prune_events_for_persist(anchors, persist=False)

    out: List[Label] = []

    # Pre-phase deps
    out.extend(secdeps)
    out.extend(deps)

    # PRE_HANDLER anchors
    _append_anchor_block(out, by_anchor, anchors, target_phase="PRE_HANDLER",
                         anchor_policies=anchor_policies, persist=persist)

    # START_TX sys (prune for non-persist)
    if persist:
        out.extend(_sorted_sys(sys_by_phase.get("START_TX", ())))
    # HANDLER anchors
    _append_anchor_block(out, by_anchor, anchors, target_phase="HANDLER",
                         anchor_policies=anchor_policies, persist=persist)

    # HANDLER sys (prune for non-persist)
    if persist:
        out.extend(_sorted_sys(sys_by_phase.get("HANDLER", ())))
    # POST_HANDLER anchors
    _append_anchor_block(out, by_anchor, anchors, target_phase="POST_HANDLER",
                         anchor_policies=anchor_policies, persist=persist)

    # END_TX sys (prune for non-persist)
    if persist:
        out.extend(_sorted_sys(sys_by_phase.get("END_TX", ())))
    # POST_RESPONSE anchors
    _append_anchor_block(out, by_anchor, anchors, target_phase="POST_RESPONSE",
                         anchor_policies=anchor_policies, persist=persist)

    # Any remaining sys in atypical phases (rare): append at the end of their phase window
    # PRE_HANDLER / POST_RESPONSE specifically
    if sys_by_phase.get("PRE_HANDLER"):
        out = _insert_after(out, after_kinds=("dep",), addition=_sorted_sys(sys_by_phase["PRE_HANDLER"]))
    if sys_by_phase.get("POST_RESPONSE"):
        out.extend(_sorted_sys(sys_by_phase["POST_RESPONSE"]))

    return out


# ──────────────────────────────────────────────────────────────────────────────
# Anchor block assembly
# ──────────────────────────────────────────────────────────────────────────────

def _append_anchor_block(
    out: List[Label],
    by_anchor: Mapping[str, Sequence[Label]],
    anchors: Sequence[str],
    *,
    target_phase: _ev.Phase,
    anchor_policies: Optional[Mapping[str, AnchorPolicy]],
    persist: bool,
) -> None:
    """Append all labels for anchors in a given phase in canonical anchor order."""
    for anchor in anchors:
        if _ev.phase_for_event(anchor) != target_phase:
            continue
        if not persist and _ev.is_persist_tied(anchor):
            continue
        group = list(by_anchor.get(anchor, ()))
        if not group:
            continue
        policy = anchor_policies.get(anchor) if anchor_policies else None
        ordered = order_within_anchor(anchor, group, policy)
        out.extend(ordered)


# ──────────────────────────────────────────────────────────────────────────────
# In-anchor ordering (topological, deterministic)
# ──────────────────────────────────────────────────────────────────────────────

def order_within_anchor(
    anchor: str,
    labels: Sequence[Label],
    policy: Optional[AnchorPolicy] = None,
) -> List[Label]:
    """
    Topologically sort labels within an anchor.

    Nodes are individual labels; edges are lifted from token-level rules where
    token = "domain:subject". If multiple labels share the same token (e.g., per-field),
    edges fan-out to all matching nodes.
    """
    # Build token index
    tokens: Dict[Label, str] = {}
    by_token: Dict[str, List[Label]] = defaultdict(list)
    for l in labels:
        if not l.domain:
            # hooks always have domain; atoms must have domain by grammar
            raise ValueError(f"In-anchor item missing domain: {l}")
        t = f"{l.domain}:{l.subject}"
        tokens[l] = t
        by_token[t].append(l)

    # Collect edges: defaults + policy
    edges = list(_DEFAULT_EDGES.get(anchor, ()))
    if policy and policy.edges:
        edges.extend(policy.edges)

    # Build adjacency on label nodes (fan-out pairwise where tokens exist)
    adj: Dict[Label, List[Label]] = {l: [] for l in labels}
    indeg: Dict[Label, int] = {l: 0 for l in labels}

    def _present(tok: str) -> bool:
        return tok in by_token

    for u_tok, v_tok in edges:
        if not (_present(u_tok) and _present(v_tok)):
            continue
        for u in by_token[u_tok]:
            for v in by_token[v_tok]:
                if v not in adj[u]:
                    adj[u].append(v)
                    indeg[v] += 1

    # Kahn topo with deterministic tie-breaks
    # Priority: policy.prefer index → DEFAULT preference index → kind (atom<hook) → domain → subject → field
    prefer = tuple(policy.prefer) if policy and policy.prefer else ()
    pref_index: Dict[str, int] = {t: i for i, t in enumerate(prefer)}
    def_pref = _PREF.get(anchor, ())
    def_index: Dict[str, int] = {t: i for i, t in enumerate(def_pref)}

    def _rank(l: Label) -> Tuple[int, int, int, str, str, str]:
        t = tokens[l]
        p1 = pref_index.get(t, 10_000)
        p2 = def_index.get(t, 10_000)
        k = 0 if l.kind == "atom" else 1  # atoms before hooks by default
        return (p1, p2, k, l.domain or "", l.subject, l.field or "")

    q: List[Label] = [n for n, d in indeg.items() if d == 0]
    q.sort(key=_rank)

    out: List[Label] = []
    while q:
        n = q.pop(0)
        out.append(n)
        for v in adj[n]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
        q.sort(key=_rank)  # keep deterministic

    if len(out) != len(labels):
        # Cycle detected — fall back to total order by rank for remaining nodes
        remaining = [n for n in labels if n not in out]
        remaining.sort(key=_rank)
        out.extend(remaining)

    return out


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def _sorted_sys(sys_labels: Sequence[Label]) -> List[Label]:
    """Deterministic ordering for system steps within the same phase."""
    return sorted(sys_labels, key=lambda l: (l.subject or "", l.field or ""))

def _insert_after(
    seq: List[Label],
    *,
    after_kinds: Tuple[str, ...],
    addition: Sequence[Label],
) -> List[Label]:
    """Insert `addition` after the last occurrence of any label with kind in after_kinds."""
    idx = -1
    for i, l in enumerate(seq):
        if l.kind in after_kinds:
            idx = i
    if idx == -1:
        return list(addition) + seq
    return seq[: idx + 1] + list(addition) + seq[idx + 1 :]


__all__ = [
    "AnchorPolicy",
    "flatten",
    "order_within_anchor",
]
