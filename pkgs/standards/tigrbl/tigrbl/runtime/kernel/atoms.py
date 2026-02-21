from __future__ import annotations

import importlib
import logging
import pkgutil
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    cast,
)

from ...op.types import PHASES, StepFn
from .. import events as _ev, ordering as _ordering, system as _sys

logger = logging.getLogger(__name__)

_AtomRun = Callable[[Optional[object], Any], Any]
_DiscoveredAtom = tuple[str, _AtomRun]


def _discover_atoms() -> list[_DiscoveredAtom]:
    out: list[_DiscoveredAtom] = []
    try:
        import tigrbl.runtime.atoms as atoms_pkg  # type: ignore
    except Exception:
        return out

    for info in pkgutil.walk_packages(atoms_pkg.__path__, atoms_pkg.__name__ + "."):  # type: ignore[attr-defined]
        if info.ispkg:
            continue
        try:
            mod = importlib.import_module(info.name)
            anchor = getattr(mod, "ANCHOR", None)
            run = getattr(mod, "run", None)
            if isinstance(anchor, str) and callable(run):
                out.append((anchor, run))
        except Exception:
            continue
    logger.debug("kernel: discovered %d atoms", len(out))
    return out


def _infer_domain_subject(run: _AtomRun) -> tuple[Optional[str], Optional[str]]:
    mod = getattr(run, "__module__", "") or ""
    parts = mod.split(".")
    try:
        i = parts.index("atoms")
        return (
            parts[i + 1] if i + 1 < len(parts) else None,
            parts[i + 2] if i + 2 < len(parts) else None,
        )
    except ValueError:
        return None, None


def _make_label(anchor: str, run: _AtomRun) -> Optional[str]:
    domain, subject = _infer_domain_subject(run)
    return f"atom:{domain}:{subject}@{anchor}" if (domain and subject) else None


def _wrap_atom(run: _AtomRun, *, anchor: str) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = run(None, ctx)
        if hasattr(rv, "__await__"):
            return await cast(Any, rv)
        return rv

    label = _make_label(anchor, run)
    if label:
        setattr(_step, "__tigrbl_label", label)
    return _step


def _hook_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, List[StepFn]] = {ph: [] for ph in PHASES}
    if alias_ns is None:
        return out
    for phase in PHASES:
        out[phase] = list(getattr(alias_ns, phase, []) or [])
    return out


def _is_persistent(chains: Mapping[str, Sequence[StepFn]]) -> bool:
    for fn in chains.get("START_TX", ()) or ():
        if getattr(fn, "__name__", "") == "start_tx":
            return True
    for fn in chains.get("PRE_TX_BEGIN", ()) or ():
        if getattr(fn, "__name__", "") == "mark_skip_persist":
            return False
    return False


def _label_dep_atom(*, subject: str, anchor: str, index: int) -> str:
    return f"atom:dep:{subject}@{anchor}#{index}"


def _make_dep_atom_step(run_fn: _AtomRun, dep: Any, *, label: str) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = run_fn(dep, ctx)
        if hasattr(rv, "__await__"):
            return await cast(Any, rv)
        return rv

    setattr(_step, "__tigrbl_label", label)
    return _step


def _inject_pre_tx_dep_atoms(chains: Dict[str, List[StepFn]], sp: Any | None) -> None:
    if sp is None:
        return
    try:
        from ..atoms.dep.security import ANCHOR as sec_anchor, run as sec_run
        from ..atoms.dep.extras import ANCHOR as dep_anchor, run as dep_run
    except Exception:
        return

    pre_tx = chains.setdefault("PRE_TX", [])
    for i, dep in enumerate(getattr(sp, "secdeps", ()) or ()):
        pre_tx.append(
            _make_dep_atom_step(
                sec_run,
                dep,
                label=_label_dep_atom(subject="security", anchor=sec_anchor, index=i),
            )
        )
    for i, dep in enumerate(getattr(sp, "deps", ()) or ()):
        pre_tx.append(
            _make_dep_atom_step(
                dep_run,
                dep,
                label=_label_dep_atom(subject="extras", anchor=dep_anchor, index=i),
            )
        )


def _inject_atoms(
    chains: Dict[str, List[StepFn]],
    atoms: Iterable[_DiscoveredAtom],
    *,
    persistent: bool,
) -> None:
    order = {name: i for i, name in enumerate(_ev.all_events_ordered())}

    def _sort_key(item: _DiscoveredAtom) -> tuple[int, int]:
        anchor, run = item
        anchor_idx = order.get(anchor, 10_000)
        domain, subject = _infer_domain_subject(run)
        token = f"{domain}:{subject}" if domain and subject else ""
        pref = _ordering._PREF.get(anchor, ())
        token_idx = pref.index(token) if token in pref else 10_000
        return anchor_idx, token_idx

    for anchor, run in sorted(atoms, key=_sort_key):
        try:
            info = _ev.get_anchor_info(anchor)
        except Exception:
            continue
        if info.phase in ("START_TX", "END_TX"):
            continue
        if not persistent and info.persist_tied:
            continue
        domain, _subject = _infer_domain_subject(run)
        if domain == "dep":
            continue

        chains.setdefault(info.phase, []).append(_wrap_atom(run, anchor=anchor))


def _inject_txn_system_steps(chains: Dict[str, List[StepFn]]) -> None:
    start_anchor, start_run = _sys.get("txn", "begin")
    end_anchor, end_run = _sys.get("txn", "commit")
    chains.setdefault(start_anchor, []).append(
        _wrap_atom(start_run, anchor=start_anchor)
    )
    chains.setdefault(end_anchor, []).append(_wrap_atom(end_run, anchor=end_anchor))
