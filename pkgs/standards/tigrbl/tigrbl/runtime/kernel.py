from __future__ import annotations

import importlib
import logging
import pkgutil
import threading
import weakref
import time
from dataclasses import dataclass
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    cast,
    Generic,
    TypeVar,
)

from .executor import _invoke, _Ctx
from . import events as _ev, ordering as _ordering, system as _sys
from ..op.types import PHASES, StepFn
from ..column.mro_collect import mro_collect_columns

logger = logging.getLogger(__name__)


K = TypeVar("K")
V = TypeVar("V")


class _WeakMaybeDict(Generic[K, V]):
    """Dictionary that uses weak references when possible.

    Falls back to strong references when ``key`` cannot be weakly referenced.
    """

    def __init__(self) -> None:
        self._weak: "weakref.WeakKeyDictionary[Any, V]" = weakref.WeakKeyDictionary()
        self._strong: Dict[int, tuple[Any, V]] = {}

    def _use_weak(self, key: Any) -> bool:
        try:
            weakref.ref(key)
            return True
        except TypeError:
            return False

    def __setitem__(self, key: K, value: V) -> None:
        if self._use_weak(key):
            self._weak[key] = value
        else:
            self._strong[id(key)] = (key, value)

    def __getitem__(self, key: K) -> V:
        if self._use_weak(key):
            return self._weak[key]
        return self._strong[id(key)][1]

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        if self._use_weak(key):
            return self._weak.get(key, default)
        return self._strong.get(id(key), (None, default))[1]

    def setdefault(self, key: K, default: V) -> V:
        if self._use_weak(key):
            return self._weak.setdefault(key, default)
        return self._strong.setdefault(id(key), (key, default))[1]

    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        if self._use_weak(key):
            return self._weak.pop(key, default)
        return self._strong.pop(id(key), (None, default))[1]


# ---- OpView shapes -------------------------------------------------


@dataclass(frozen=True)
class SchemaIn:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]


@dataclass(frozen=True)
class SchemaOut:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]
    expose: Tuple[str, ...]


@dataclass(frozen=True)
class OpView:
    schema_in: SchemaIn
    schema_out: SchemaOut
    paired_index: Dict[str, Dict[str, object]]
    virtual_producers: Dict[str, Callable[[object, dict], object]]
    to_stored_transforms: Dict[str, Callable[[object, dict], object]]
    refresh_hints: Tuple[str, ...]


# ──────────────────────────── Discovery ────────────────────────────

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
        setattr(_step, "__tigrbl_label", label)
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

    def _sort_key(item: _DiscoveredAtom) -> tuple[int, int]:
        anchor, run = item
        anchor_idx = order.get(anchor, 10_000)
        d, s = _infer_domain_subject(run)
        token = f"{d}:{s}" if d and s else ""
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
        chains.setdefault(info.phase, []).append(_wrap_atom(run, anchor=anchor))


# ───────────────────────────── Kernel ──────────────────────────────


class Kernel:
    """
    SSoT for runtime scheduling. One Kernel per App (not per API).
    Auto-primed under the hood. Downstream users never touch this.
    """

    _instance: ClassVar["Kernel | None"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Kernel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None):
        if atoms is None and getattr(self, "_singleton_initialized", False):
            self._reset(atoms)
            return
        self._reset(atoms)
        if atoms is None:
            self._singleton_initialized = True

    def _reset(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None) -> None:
        self._atoms_cache = list(atoms) if atoms else None
        self._specs_cache = _SpecsOnceCache()
        self._opviews = _WeakMaybeDict()
        self._kernelz_payload = _WeakMaybeDict()
        self._primed = _WeakMaybeDict()
        self._lock = threading.Lock()

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
        specs = getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {})
        sp_list = specs.get(alias) or ()
        sp = sp_list[0] if sp_list else None
        target = (getattr(sp, "target", alias) or "").lower()
        persist_policy = getattr(sp, "persist", "default")
        persistent = (
            persist_policy != "skip" and target not in {"read", "list"}
        ) or _is_persistent(chains)
        try:
            _inject_atoms(chains, self._atoms() or (), persistent=persistent)
        except Exception:
            logger.exception(
                "kernel: atom injection failed for %s.%s",
                getattr(model, "__name__", model),
                alias,
            )
        if persistent:
            try:
                start_anchor, start_run = _sys.get("txn", "begin")
                end_anchor, end_run = _sys.get("txn", "commit")
                chains.setdefault(start_anchor, []).append(
                    _wrap_atom(start_run, anchor=start_anchor)
                )
                chains.setdefault(end_anchor, []).append(
                    _wrap_atom(end_run, anchor=end_anchor)
                )
            except Exception:
                logger.exception(
                    "kernel: failed to inject txn system steps for %s.%s",
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
                lbl = getattr(step, "__tigrbl_label", None)
                if isinstance(lbl, str) and lbl.endswith(f"@{anchor}"):
                    labels.append(lbl)
        return labels

    async def invoke(
        self,
        *,
        model: type,
        alias: str,
        db: Any,
        request: Any | None = None,
        ctx: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Execute an operation for ``model.alias`` using the executor."""
        phases = self.build(model, alias)
        base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        base_ctx.model = model
        base_ctx.op = alias
        specs = self.get_specs(model)
        base_ctx.opview = self._compile_opview_from_specs(
            specs, SimpleNamespace(alias=alias)
        )
        return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)

    # ——— per-App autoprime (hidden) ———
    def ensure_primed(self, app: Any) -> None:
        """Autoprime once per App: specs → OpViews → /kernelz payload."""
        with self._lock:
            if self._primed.get(app):
                return
            from ..system.diagnostics.utils import (
                model_iter as _model_iter,
                opspecs as _opspecs,
            )

            models = list(_model_iter(app))

            # 1) per-model specs once
            for m in models:
                self._specs_cache.get(m)

            # 2) compile OpViews per (model, alias)
            ov_map: Dict[Tuple[type, str], OpView] = {}
            for m in models:
                specs = self._specs_cache.get(m)
                for sp in _opspecs(m):
                    ov_map[(m, sp.alias)] = self._compile_opview_from_specs(specs, sp)
            self._opviews[app] = ov_map

            # 3) build /kernelz payload once (dedup wire hooks)
            payload = self._build_kernelz_payload_internal(app)
            self._kernelz_payload[app] = payload
            self._primed[app] = True

    def get_opview(self, app: Any, model: type, alias: str) -> OpView:
        """Return OpView for (model, alias); compile on-demand if missing."""
        ov_map = self._opviews.get(app)
        if isinstance(ov_map, dict):
            ov = ov_map.get((model, alias))
            if ov is not None:
                return ov

        self.ensure_primed(app)

        ov_map = self._opviews.setdefault(app, {})
        ov = ov_map.get((model, alias))
        if ov is not None:
            return ov

        try:
            specs = self._specs_cache.get(model)
            from types import SimpleNamespace
            from ..system.diagnostics.utils import opspecs as _opspecs

            found = False
            for sp in _opspecs(model):
                ov_map.setdefault(
                    (model, sp.alias), self._compile_opview_from_specs(specs, sp)
                )
                if sp.alias == alias:
                    found = True

            if not found:
                temp_sp = SimpleNamespace(alias=alias)
                ov_map[(model, alias)] = self._compile_opview_from_specs(specs, temp_sp)

            return ov_map[(model, alias)]
        except Exception:
            raise RuntimeError(
                f"opview_missing: app={app!r} model={getattr(model, '__name__', model)!r} alias={alias!r}"
            )

    def kernelz_payload(self, app: Any) -> Dict[str, Dict[str, List[str]]]:
        """Thin accessor for endpoint: guarantees primed, returns cached payload."""
        self.ensure_primed(app)
        return self._kernelz_payload[app]

    def invalidate_kernelz_payload(self, app: Optional[Any] = None) -> None:
        with self._lock:
            if app is None:
                self._kernelz_payload = _WeakMaybeDict()
                self._opviews = _WeakMaybeDict()
                self._primed = _WeakMaybeDict()
            else:
                self._kernelz_payload.pop(app, None)
                self._opviews.pop(app, None)
                self._primed.pop(app, None)

    def _compile_opview_from_specs(self, specs: Mapping[str, Any], sp: Any) -> OpView:
        """Build a basic OpView from collected specs when no app/model is present."""
        alias = getattr(sp, "alias", "")

        in_fields: list[str] = []
        out_fields: list[str] = []
        by_field_in: Dict[str, Dict[str, object]] = {}
        by_field_out: Dict[str, Dict[str, object]] = {}

        for name, spec in specs.items():
            io = getattr(spec, "io", None)
            fs = getattr(spec, "field", None)
            storage = getattr(spec, "storage", None)
            in_verbs = set(getattr(io, "in_verbs", ()) or ())
            out_verbs = set(getattr(io, "out_verbs", ()) or ())

            if alias in in_verbs:
                in_fields.append(name)
                meta: Dict[str, object] = {"in_enabled": True}
                if storage is None:
                    meta["virtual"] = True
                df = getattr(spec, "default_factory", None)
                if callable(df):
                    meta["default_factory"] = df
                alias_in = getattr(io, "alias_in", None)
                if alias_in:
                    meta["alias_in"] = alias_in
                required = bool(fs and alias in getattr(fs, "required_in", ()))
                meta["required"] = required
                base_nullable = (
                    True if storage is None else getattr(storage, "nullable", True)
                )
                meta["nullable"] = base_nullable
                by_field_in[name] = meta

            if alias in out_verbs:
                out_fields.append(name)
                meta_out: Dict[str, object] = {}
                alias_out = getattr(io, "alias_out", None)
                if alias_out:
                    meta_out["alias_out"] = alias_out
                if storage is None:
                    meta_out["virtual"] = True
                py_t = getattr(getattr(fs, "py_type", None), "__name__", None)
                if py_t:
                    meta_out["py_type"] = py_t
                by_field_out[name] = meta_out

        schema_in = SchemaIn(
            fields=tuple(sorted(in_fields)),
            by_field={f: by_field_in.get(f, {}) for f in sorted(in_fields)},
        )
        schema_out = SchemaOut(
            fields=tuple(sorted(out_fields)),
            by_field={f: by_field_out.get(f, {}) for f in sorted(out_fields)},
            expose=tuple(sorted(out_fields)),
        )
        paired_index: Dict[str, Dict[str, object]] = {}
        for field, col in specs.items():
            io = getattr(col, "io", None)
            cfg = getattr(io, "_paired", None)
            if cfg and sp.alias in getattr(cfg, "verbs", ()):  # type: ignore[attr-defined]
                field_spec = getattr(col, "field", None)
                max_len = None
                if field_spec is not None:
                    max_len = getattr(
                        getattr(field_spec, "constraints", {}),
                        "get",
                        lambda k, d=None: None,
                    )("max_length")
                paired_index[field] = {
                    "alias": cfg.alias,
                    "gen": cfg.gen,
                    "store": cfg.store,
                    "mask_last": cfg.mask_last,
                    "max_length": max_len,
                }

        return OpView(
            schema_in=schema_in,
            schema_out=schema_out,
            paired_index=paired_index,
            virtual_producers={},
            to_stored_transforms={},
            refresh_hints=(),
        )

    # ——— internal: endpoint-ready payload (once per App) ———
    def _build_kernelz_payload_internal(
        self, app: Any
    ) -> Dict[str, Dict[str, List[str]]]:
        from ..system.diagnostics.utils import (
            model_iter as _model_iter,
            opspecs as _opspecs,
            label_callable as _label_callable,
            label_hook as _label_hook,
        )

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
                        lbl = getattr(step, "__tigrbl_label", None)
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
