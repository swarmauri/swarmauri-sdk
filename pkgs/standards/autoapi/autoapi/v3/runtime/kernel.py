from __future__ import annotations

import importlib
import logging
import pkgutil
import threading
import weakref
import time
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

from .executor import _invoke, _Ctx
from . import events as _ev
from ..op.types import PHASES, StepFn
from ..column.mro_collect import mro_collect_columns

logger = logging.getLogger(__name__)

# ──────────────────────────── Discovery ────────────────────────────

_AtomRun = Callable[[Optional[object], Any], Any]
_DiscoveredAtom = tuple[str, _AtomRun]


def _discover_atoms() -> list[_DiscoveredAtom]:
    out: list[_DiscoveredAtom] = []
    try:
        import autoapi.v3.runtime.atoms as atoms_pkg  # type: ignore
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


# ──────────────────────────── Labeling ─────────────────────────────


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
    d, s = _infer_domain_subject(run)
    return f"atom:{d}:{s}@{anchor}" if (d and s) else None


def _wrap_atom(run: _AtomRun, *, anchor: str) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = run(None, ctx)
        if hasattr(rv, "__await__"):
            return await cast(Any, rv)
        return rv

    label = _make_label(anchor, run)
    if label:
        setattr(_step, "__autoapi_label", label)
    return _step


# ──────────────────────────── Specs cache (once) ────────────────────


class _SpecsOnceCache:
    """Thread-safe, compute-once cache of per-model column specs."""

    def __init__(self) -> None:
        self._d: Dict[type, Mapping[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, model: type) -> Mapping[str, Any]:
        try:
            return self._d[model]
        except KeyError:
            pass
        with self._lock:
            rv = self._d.get(model)
            if rv is None:
                rv = mro_collect_columns(model)
                self._d[model] = rv
        return rv

    def prime(self, models: Sequence[type]) -> None:
        for m in models:
            self.get(m)

    def invalidate(self, model: Optional[type] = None) -> None:
        with self._lock:
            if model is None:
                self._d.clear()
            else:
                self._d.pop(model, None)


# ──────────────────────────── Hooks & Phases ────────────────────────


def _hook_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, List[StepFn]] = {ph: [] for ph in PHASES}
    if alias_ns is None:
        return out
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _is_persistent(chains: Mapping[str, Sequence[StepFn]]) -> bool:
    for fn in chains.get("START_TX", ()) or ():
        if getattr(fn, "__name__", "") == "start_tx":
            return True
    for fn in chains.get("PRE_TX_BEGIN", ()) or ():
        if getattr(fn, "__name__", "") == "mark_skip_persist":
            return False
    return False


def _inject_atoms(
    chains: Dict[str, List[StepFn]],
    atoms: Iterable[_DiscoveredAtom],
    *,
    persistent: bool,
) -> None:
    order = {name: i for i, name in enumerate(_ev.all_events_ordered())}
    for anchor, run in sorted(atoms, key=lambda it: order.get(it[0], 10_000)):
        try:
            info = _ev.get_anchor_info(anchor)
        except Exception:
            continue
        if info.phase in ("START_TX", "END_TX"):
            continue
        if not persistent and info.persist_tied:
            continue
        chains.setdefault(info.phase, []).append(_wrap_atom(run, anchor=anchor))


# ───────────────────────────── Kernel ──────────────────────────────


class Kernel:
    """
    SSoT for runtime scheduling. One Kernel per App (not per API).
    Auto-primed under the hood. Downstream users never touch this.
    """

    def __init__(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None):
        self._atoms_cache: Optional[list[_DiscoveredAtom]] = (
            list(atoms) if atoms else None
        )
        self._specs_cache = _SpecsOnceCache()
        # App-scoped payload cache (no leaks if App is GC’d)
        self._app_payload_cache: "weakref.WeakKeyDictionary[Any, Dict[str, Dict[str, List[str]]]]" = weakref.WeakKeyDictionary()
        self._app_primed: "weakref.WeakKeyDictionary[Any, bool]" = (
            weakref.WeakKeyDictionary()
        )
        self._prime_lock = threading.Lock()

    # ——— atoms ———
    def _atoms(self) -> list[_DiscoveredAtom]:
        if self._atoms_cache is None:
            self._atoms_cache = _discover_atoms()
        return self._atoms_cache

    # ——— specs cache (maintainers only; used internally) ———
    def get_specs(self, model: type) -> Mapping[str, Any]:
        return self._specs_cache.get(model)

    def prime_specs(self, models: Sequence[type]) -> None:
        self._specs_cache.prime(models)

    def invalidate_specs(self, model: Optional[type] = None) -> None:
        self._specs_cache.invalidate(model)

    # ——— build / plan ———
    def build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
        chains = _hook_phase_chains(model, alias)
        persistent = (alias or "").lower() in {
            "create",
            "update",
            "replace",
            "delete",
        } or _is_persistent(chains)
        try:
            _inject_atoms(chains, self._atoms() or (), persistent=persistent)
        except Exception:
            logger.exception(
                "kernel: atom injection failed for %s.%s",
                getattr(model, "__name__", model),
                alias,
            )
        for ph in PHASES:
            chains.setdefault(ph, [])
        return chains

    def plan_labels(self, model: type, alias: str) -> list[str]:
        labels: list[str] = []
        chains = self.build(model, alias)
        ordered_anchors = _ev.all_events_ordered()
        phase_for = {a: _ev.get_anchor_info(a).phase for a in ordered_anchors}
        for anchor in ordered_anchors:
            phase = phase_for[anchor]
            for step in chains.get(phase, []) or []:
                lbl = getattr(step, "__autoapi_label", None)
                if isinstance(lbl, str) and lbl.endswith(f"@{anchor}"):
                    labels.append(lbl)
        return labels

    # ——— per-App autoprime (hidden) ———
    def ensure_primed(self, app: Any) -> None:
        """
        Idempotent: primes once per App.
        • primes specs for all models in the App
        • builds and caches the final /kernelz payload
        """
        with self._prime_lock:
            if self._app_primed.get(app):
                return
            from ..app.system import _model_iter  # re-use existing enumeration helpers

            models = list(_model_iter(app))
            start = time.monotonic()
            self.prime_specs(models)
            payload = self._build_kernelz_payload_internal(app)
            self._app_payload_cache[app] = payload
            self._app_primed[app] = True
            duration = time.monotonic() - start
            logger.debug(
                "kernel: primed app %s in %.3fs (models=%d)", app, duration, len(models)
            )

    def kernelz_payload(self, app: Any) -> Dict[str, Dict[str, List[str]]]:
        """Thin accessor for endpoint: guarantees primed, returns cached payload."""
        self.ensure_primed(app)
        return self._app_payload_cache[app]

    def invalidate_kernelz_payload(self, app: Optional[Any] = None) -> None:
        with self._prime_lock:
            if app is None:
                self._app_payload_cache = weakref.WeakKeyDictionary()
                self._app_primed = weakref.WeakKeyDictionary()
            else:
                self._app_payload_cache.pop(app, None)
                self._app_primed.pop(app, None)

    # ——— internal: endpoint-ready payload (once per App) ———
    def _build_kernelz_payload_internal(
        self, app: Any
    ) -> Dict[str, Dict[str, List[str]]]:
        from ..app.system import (
            _model_iter,
            _opspecs,
            _label_callable,
            _label_hook,
        )  # reuse

        start = time.monotonic()
        out: Dict[str, Dict[str, List[str]]] = {}
        for model in _model_iter(app):
            self.get_specs(model)  # ensure cached
            mname = getattr(model, "__name__", "Model")
            model_map: Dict[str, List[str]] = {}
            for sp in _opspecs(model):
                seq: List[str] = []

                # PRE_TX: secdeps / deps
                secdeps = [
                    _label_callable(d) if callable(d) else str(d)
                    for d in (getattr(sp, "secdeps", []) or [])
                ]
                deps = [
                    _label_callable(d) if callable(d) else str(d)
                    for d in (getattr(sp, "deps", []) or [])
                ]
                seq.extend(f"PRE_TX:secdep:{s}" for s in secdeps)
                seq.extend(f"PRE_TX:dep:{d}" for d in deps)

                # Chains and system hooks in canonical phase order
                chains = self.build(model, sp.alias)
                persist = getattr(sp, "persist", "default") != "skip"

                for ph in PHASES:
                    if ph == "START_TX" and persist:
                        seq.append("START_TX:hook:sys:txn:begin@START_TX")

                    for step in chains.get(ph, []) or []:
                        lbl = getattr(step, "__autoapi_label", None)
                        seq.append(
                            f"{ph}:{lbl}"
                            if isinstance(lbl, str)
                            else f"{ph}:{_label_hook(step, ph)}"
                        )

                    if ph == "END_TX" and persist:
                        seq.append("END_TX:hook:sys:txn:commit@END_TX")

                # De-dup wire hooks (memory/perf friendly)
                seen, dedup = set(), []
                for lbl in seq:
                    if ":hook:wire:" in lbl:
                        if lbl in seen:
                            continue
                        seen.add(lbl)
                    dedup.append(lbl)

                model_map[sp.alias] = dedup

            if model_map:
                out[mname] = model_map
        duration = time.monotonic() - start
        logger.debug("kernel: built kernelz payload for app %s in %.3fs", app, duration)
        return out


# ───────────────────────── Module-level exports ────────────────────

_default_kernel = Kernel()


def get_cached_specs(model: type) -> Mapping[str, Any]:
    """Atoms can call this; zero per-request collection."""
    return _default_kernel.get_specs(model)


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
    phases = _default_kernel.build(model, alias)
    base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


__all__ = ["Kernel", "get_cached_specs", "_default_kernel", "build_phase_chains", "run"]
