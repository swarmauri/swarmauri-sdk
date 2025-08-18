# autoapi/v3/runtime/kernel.py
from __future__ import annotations

import importlib
import logging
import pkgutil
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Mapping, Optional, Sequence

from .executor import _invoke, _Ctx
from . import events as _ev
from ..opspec.types import PHASES, StepFn

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Atom discovery
# ───────────────────────────────────────────────────────────────────────────────

_AtomRun = Callable[[Optional[object], Any], Any]  # def run(obj, ctx) -> Any
_DiscoveredAtom = tuple[str, _AtomRun]             # (anchor, run)

def _discover_atoms() -> list[_DiscoveredAtom]:
    """
    Walk the autoapi.v3.runtime.atoms package and collect (ANCHOR, run) pairs.
    Silently skips modules that fail to import or lack the expected symbols.
    """
    out: list[_DiscoveredAtom] = []
    try:
        import autoapi.v3.runtime.atoms as atoms_pkg  # type: ignore
    except Exception:
        return out

    for info in pkgutil.walk_packages(atoms_pkg.__path__, atoms_pkg.__name__ + "."):  # type: ignore[attr-defined]
        if info.ispkg:
            continue
        mod = None
        try:
            mod = importlib.import_module(info.name)
            anchor = getattr(mod, "ANCHOR", None)
            run = getattr(mod, "run", None)
            if isinstance(anchor, str) and callable(run):
                out.append((anchor, run))
        except Exception:
            # Never let a single module break discovery.
            continue
        finally:
            mod = None
    return out


def _wrap_atom(run: _AtomRun) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = run(None, ctx)
        if hasattr(rv, "__await__"):
            return await rv  # type: ignore[misc]
        return rv

    _step.__name__ = getattr(run, "__name__", "atom")
    _step.__qualname__ = getattr(run, "__qualname__", _step.__name__)
    return _step


# ───────────────────────────────────────────────────────────────────────────────
# Phase-chain helpers
# ───────────────────────────────────────────────────────────────────────────────

def _hook_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    """
    Return a copy of {phase: [step, ...]} from model.hooks.<alias>,
    ensuring all PHASES keys are present.
    """
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, List[StepFn]] = {ph: [] for ph in PHASES}
    if alias_ns is None:
        return out
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _is_persistent(chains: Mapping[str, Sequence[StepFn]]) -> bool:
    """
    Heuristic:
      • if START_TX contains a default 'start_tx' step → persistent
      • if PRE_TX_BEGIN contains 'mark_skip_persist' → ephemeral (non-persistent)
      • else default False (read-only)
    """
    for fn in chains.get("START_TX", ()) or ():
        if getattr(fn, "__name__", "") == "start_tx":
            return True
    for fn in chains.get("PRE_TX_BEGIN", ()) or ():
        if getattr(fn, "__name__", "") == "mark_skip_persist":
            return False
    return False


def _inject_atoms(chains: Dict[str, List[StepFn]], atoms: Iterable[_DiscoveredAtom], *, persistent: bool) -> None:
    """
    Append atom steps into the appropriate phase chains, preserving the global
    anchor order defined by runtime.events. START_TX/END_TX never get atoms.
    """
    # Order anchors canonically
    order = {name: i for i, name in enumerate(_ev.all_events_ordered())}

    # Sort discovered atoms by canonical anchor ordering
    discovered = sorted(atoms, key=lambda it: order.get(it[0], 10_000))

    for anchor, run in discovered:
        try:
            info = _ev.get_anchor_info(anchor)
        except Exception:
            continue
        if info.phase in ("START_TX", "END_TX"):
            continue
        if not persistent and info.persist_tied:
            continue
        chains.setdefault(info.phase, [])
        chains[info.phase].append(_wrap_atom(run))


# ───────────────────────────────────────────────────────────────────────────────
# Kernel
# ───────────────────────────────────────────────────────────────────────────────

class Kernel:
    """
    Phase-chain builder and executor façade.

    • build(model, alias)  → {phase: [StepFn, ...]}
    • invoke(model, alias, *, db, request=None, ctx=None) → Any
    """

    def __init__(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None):
        self._atoms: Optional[list[_DiscoveredAtom]] = list(atoms) if atoms is not None else None

    def _atoms(self) -> list[_DiscoveredAtom]:
        if self._atoms is None:
            # Cache discovery result
            self._atoms = _discover_atoms()
        return self._atoms

    def build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
        chains = _hook_phase_chains(model, alias)
        persistent = _is_persistent(chains)
        try:
            _inject_atoms(chains, self._atoms() or (), persistent=persistent)
        except Exception:
            # Never let atom injection break the core pipeline
            logger.exception("kernel: atom injection failed for %s.%s", getattr(model, "__name__", model), alias)
        # Ensure all phases exist
        for ph in PHASES:
            chains.setdefault(ph, [])
        return chains

    async def invoke(
        self,
        *,
        model: type,
        alias: str,
        db: Any,
        request: Any | None = None,
        ctx: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        phases = self.build(model, alias)
        base_ctx = _Ctx.from_request(request, db=db, seed=ctx)
        try:
            base_ctx.method = alias
        except Exception:
            pass
        try:
            base_ctx.model = getattr(model, "__name__", str(model))
        except Exception:
            pass
        return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


# module-level convenience
_default_kernel = Kernel()

def build_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    return _default_kernel.build(model, alias)

async def run(
    model: type,
    alias: str,
    *,
    db: Any,
    request: Any | None = None,
    ctx: Optional[Mapping[str, Any]] = None,
) -> Any:
    return await _default_kernel.invoke(model=model, alias=alias, db=db, request=request, ctx=ctx)


__all__ = ["Kernel", "build_phase_chains", "run"]
