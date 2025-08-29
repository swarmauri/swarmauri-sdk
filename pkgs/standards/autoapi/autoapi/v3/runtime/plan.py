# autoapi/v3/runtime/plan.py
from __future__ import annotations

from dataclasses import dataclass
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
    Tuple,
)

from . import events as _ev
from . import labels as _lbl
from . import ordering as _ord


# ──────────────────────────────────────────────────────────────────────────────
# Public datatypes
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AtomNode:
    """
    A single executable atom instance bound to a (model, anchor[, field]).
    """

    label: _lbl.Label  # atom:domain:subject@anchor[#field]
    run: Callable[..., Any]  # (obj|None, ctx) -> None/Mutation
    domain: str
    subject: str
    anchor: str
    field: Optional[str] = None  # per-field instance suffix (diagnostics)


@dataclass(frozen=True)
class Plan:
    """
    A compiled, per-model plan of atoms.
    System steps (txn begin/commit/handler) are executor-owned; we only inject
    their labels at render/flatten time for diagnostics.
    """

    model_name: str
    atoms_by_anchor: Dict[str, Tuple[AtomNode, ...]]
    # Optional pre-phase deps/secdeps (router-level). Only labels are kept here.
    secdeps: Tuple[_lbl.Label, ...] = ()
    deps: Tuple[_lbl.Label, ...] = ()

    def labels(self) -> List[_lbl.Label]:
        """All atom labels (unsorted) for quick diagnostics."""
        out: List[_lbl.Label] = []
        for nodes in self.atoms_by_anchor.values():
            out.extend(n.label for n in nodes)
        return out


# ──────────────────────────────────────────────────────────────────────────────
# Entry points
# ──────────────────────────────────────────────────────────────────────────────


def attach_atoms_for_model(
    model: Any,
    specs: Mapping[str, Any],
    *,
    only_keys: Optional[Sequence[str]] = None,
) -> Plan:
    """
    Build the atom plan for `model` from ColumnSpecs and attach it at
    `model._autoapi_plan`. Returns the created Plan.

    `specs` is expected to be a mapping {field_name -> ColumnSpec}.
    If `only_keys` is provided, restrict per-field instantiation to that subset.
    """
    plan = build_plan(model, specs, only_keys=only_keys)

    # Attach for easy access from executor/bindings/diagnostics
    setattr(model, "_autoapi_plan", plan)
    # Optional: a tiny namespace with convenience views
    setattr(model, "runtime", SimpleNamespace(plan=plan))

    return plan


def build_plan(
    model: Any,
    specs: Mapping[str, Any],
    *,
    only_keys: Optional[Sequence[str]] = None,
) -> Plan:
    """
    Compile a Plan by reading atom registrations and instantiating per-model / per-field atoms.
    """
    model_name = getattr(model, "__name__", str(model))

    # Import registry lazily to avoid import cycles during package init
    try:
        from .atoms import REGISTRY as _ATOM_REGISTRY  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "runtime.atoms.REGISTRY is not available; ensure runtime/atoms/__init__.py "
            "exports REGISTRY = { (domain, subject): (anchor, runner) }"
        ) from e

    # Normalize field filter
    only: Optional[set[str]] = set(only_keys) if only_keys else None

    # Field inventory from ColumnSpecs
    fields = sorted(specs.keys())
    if only is not None:
        fields = [f for f in fields if f in only]

    # Partition atoms into per-model vs per-field subjects
    per_field_subjects = {
        # schema
        ("schema", "collect_in"),
        # wire (contract → wire)
        ("wire", "build_in"),
        ("wire", "validate"),  # canonical subject (alias of validate_in)
        ("wire", "validate_in"),  # accept old name if registrar exports it
        ("wire", "build_out"),
        ("wire", "dump"),
        # storage / out
        ("storage", "to_stored"),
        ("out", "masking"),
    }
    # The rest of the registered atoms are treated as per-model.

    atoms_by_anchor: Dict[str, List[AtomNode]] = {
        a: [] for a in _ev.all_events_ordered()
    }

    # 1) Per-model atoms (single instance)
    for (domain, subject), (anchor, runner) in _ATOM_REGISTRY.items():
        if (domain, subject) in per_field_subjects:
            continue  # handled below
        _ensure_known_anchor(anchor, domain, subject)
        node = AtomNode(
            label=_lbl.make_atom(domain, subject, anchor),
            run=runner,
            domain=domain,
            subject=subject,
            anchor=anchor,
            field=None,
        )
        atoms_by_anchor[anchor].append(node)

    # 2) Per-field atoms (one instance per field, with #field suffix)
    for (domain, subject), (anchor, runner) in _ATOM_REGISTRY.items():
        if (domain, subject) not in per_field_subjects:
            continue
        _ensure_known_anchor(anchor, domain, subject)
        for field in fields:
            col = specs[field]
            if not _should_instantiate(domain, subject, anchor, field, col):
                continue
            node = AtomNode(
                label=_lbl.make_atom(domain, subject, anchor, field=field),
                run=runner,
                domain=domain,
                subject=subject,
                anchor=anchor,
                field=field,
            )
            atoms_by_anchor[anchor].append(node)

    # Freeze to tuples and drop anchors with no atoms to keep plan compact
    frozen: Dict[str, Tuple[AtomNode, ...]] = {}
    for anchor, items in atoms_by_anchor.items():
        if items:
            frozen[anchor] = tuple(items)

    return Plan(model_name=model_name, atoms_by_anchor=frozen)


def flattened_order(
    plan: Plan,
    *,
    persist: bool,
    include_system_steps: bool = True,
    secdeps: Iterable[str] | Iterable[_lbl.Label] = (),
    deps: Iterable[str] | Iterable[_lbl.Label] = (),
    anchor_policies: Optional[Mapping[str, _ord.AnchorPolicy]] = None,
) -> List[_lbl.Label]:
    """
    Compute a flattened list of labels for diagnostics/execution preview.

    - Injects optional secdep/dep labels (strings auto-wrapped).
    - Injects system step labels (txn begin/handler/commit) when requested and persist=True.
    - Applies persist pruning and deterministic ordering via runtime.ordering.flatten().
    """
    # 1) Base atom labels
    atom_labels: List[_lbl.Label] = []
    for nodes in plan.atoms_by_anchor.values():
        atom_labels.extend(n.label for n in nodes)

    # 2) Optional deps/secdeps
    secdep_labels = [_ensure_label(x, kind="secdep") for x in secdeps]
    dep_labels = [_ensure_label(x, kind="dep") for x in deps]

    # 3) Optional system steps (labels only; executor owns behavior)
    sys_labels: List[_lbl.Label] = []
    if include_system_steps and persist:
        sys_labels.extend(
            [
                _lbl.make_sys("txn:begin", "START_TX"),
                _lbl.make_sys("handler:crud", "HANDLER"),
                _lbl.make_sys("txn:commit", "END_TX"),
            ]
        )

    # 4) Flatten using canonical ordering
    return _ord.flatten(
        tuple(secdep_labels + dep_labels + sys_labels + atom_labels),
        persist=persist,
        anchor_policies=anchor_policies,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _should_instantiate(
    domain: str, subject: str, anchor: str, field: str, col: Any
) -> bool:
    """Return True if a per-field atom should be instantiated.

    This conservative placeholder always returns ``True`` and can be expanded
    with domain-specific logic in the future.
    """

    return True


def _ensure_known_anchor(anchor: str, domain: str, subject: str) -> None:
    if not _ev.is_valid_event(anchor):
        raise ValueError(
            f"Atom ({domain}:{subject}) declares unknown anchor {anchor!r}"
        )


def _ensure_label(x: str | _lbl.Label, *, kind: str) -> _lbl.Label:
    if isinstance(x, _lbl.Label):
        return x
    if kind == "secdep":
        return _lbl.make_secdep(x)
    if kind == "dep":
        return _lbl.make_dep(x)
    raise ValueError(f"Unsupported label kind: {kind}")
