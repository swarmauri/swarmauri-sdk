from __future__ import annotations

import logging
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping

from tigrbl_atoms import StepFn
from tigrbl_atoms.atoms.sys.phase_db import run as _bind_phase_db

from . import events as _ev
from .atoms import (
    _hook_phase_chains,
    _inject_atoms,
    _inject_pre_tx_dep_atoms,
    _is_persistent,
    _wrap_atom,
)
from .models import KernelPlan, OpKey, PackedKernel
from .types import (
    EGRESS_PHASES,
    INGRESS_PHASES,
    LOWER_KIND_ASYNC_DIRECT,
    LOWER_KIND_SPLIT_EXTRACTABLE,
    LOWER_KIND_SYNC_EXTRACTABLE,
)
from .utils import (
    _classify_step_lowering,
    _effect_descriptor_for_step,
    _label_step,
    _opspecs,
)

logger = logging.getLogger(__name__)


_PHASE_DB_LABEL = "atom:sys:phase_db@SYS_PHASE_DB_BIND"


def _phase_db_step() -> StepFn:
    step = _wrap_atom(_bind_phase_db, anchor="SYS_PHASE_DB_BIND")
    setattr(step, "__tigrbl_label", _PHASE_DB_LABEL)
    return step


def _prepend_phase_db_binding(
    chains: Dict[str, List[StepFn]],
    phases: tuple[str, ...] | list[str],
) -> None:
    for phase in phases:
        steps = list(chains.get(phase, ()) or ())
        if steps and getattr(steps[0], "__tigrbl_label", None) == _PHASE_DB_LABEL:
            chains[phase] = steps
            continue
        chains[phase] = [_phase_db_step(), *steps]


def _build_op(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
    from .core import DEFAULT_PHASE_ORDER

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
        _inject_atoms(
            chains,
            self._atoms() or (),
            persistent=persistent,
            target=target,
        )
    except Exception:
        logger.exception(
            "kernel: atom injection failed for %s.%s",
            getattr(model, "__name__", model),
            alias,
        )

    _inject_pre_tx_dep_atoms(chains, sp)

    for phase in DEFAULT_PHASE_ORDER:
        chains.setdefault(phase, [])
    _prepend_phase_db_binding(chains, list(DEFAULT_PHASE_ORDER))
    return chains


def _build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
    return self._build_op(model, alias)


def _build_ingress(self, app: Any) -> Dict[str, List[StepFn]]:
    del app
    order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
    ingress_atoms: Dict[str, List[tuple[str, Any]]] = {}
    for anchor, run in self._atoms() or ():
        if not _ev.is_valid_event(anchor):
            continue
        phase = _ev.phase_for_event(anchor)
        if phase not in INGRESS_PHASES:
            continue
        ingress_atoms.setdefault(phase, []).append((anchor, run))

    out: Dict[str, List[StepFn]] = {}
    for phase, atoms in ingress_atoms.items():
        ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
        out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
    for phase in INGRESS_PHASES:
        out.setdefault(phase, [])
    _prepend_phase_db_binding(out, list(INGRESS_PHASES))
    return out


def _build_egress(self, app: Any) -> Dict[str, List[StepFn]]:
    del app
    order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
    egress_atoms: Dict[str, List[tuple[str, Any]]] = {}
    for anchor, run in self._atoms() or ():
        if not _ev.is_valid_event(anchor):
            continue
        phase = _ev.phase_for_event(anchor)
        if phase not in EGRESS_PHASES:
            continue
        egress_atoms.setdefault(phase, []).append((anchor, run))

    out: Dict[str, List[StepFn]] = {}
    for phase, atoms in egress_atoms.items():
        ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
        out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
    for phase in EGRESS_PHASES:
        out.setdefault(phase, [])
    _prepend_phase_db_binding(out, list(EGRESS_PHASES))
    return out


def _plan_labels(self, model: type, alias: str) -> list[str]:
    from .core import DEFAULT_PHASE_ORDER

    labels: list[str] = []
    chains = self._build(model, alias)
    opspec = next(
        (sp for sp in _opspecs(model) if getattr(sp, "alias", None) == alias),
        None,
    )
    persist = getattr(opspec, "persist", "default") != "skip"

    tx_begin = "START_TX:hook:sys:txn:begin@START_TX"
    tx_end = "END_TX:hook:sys:txn:commit@END_TX"
    if persist:
        labels.append(tx_begin)

    def _display_phase(phase: str, step_label: str) -> str:
        if phase != "POST_COMMIT":
            return phase
        if "@out:build" in step_label:
            return "POST_HANDLER"
        if "@out:dump" in step_label:
            return "POST_RESPONSE"
        return phase

    for phase in DEFAULT_PHASE_ORDER:
        if phase in {"START_TX", "END_TX"}:
            continue
        for step in chains.get(phase, ()) or ():
            step_label = _label_step(step, phase)
            if "SYS_PHASE_DB_BIND" in str(step_label):
                continue
            labels.append(f"{_display_phase(phase, step_label)}:{step_label}")

    if persist:
        labels.append(tx_end)

    return labels


def _segment_label(self, program_id: int, phase: str) -> str:
    return f"program:{program_id}:{phase}"


def _build_route_matrix(
    self,
    *,
    proto_names: tuple[str, ...],
    selector_names: tuple[str, ...],
    opkey_to_meta: Mapping[OpKey, int],
) -> tuple[tuple[int, ...], ...]:
    proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
    selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
    matrix = [[-1 for _ in selector_names] for _ in proto_names]
    for key, meta_index in opkey_to_meta.items():
        proto_id = proto_to_id.get(key.proto)
        selector_id = selector_to_id.get(key.selector)
        if proto_id is None or selector_id is None:
            continue
        matrix[proto_id][selector_id] = int(meta_index)
    return tuple(tuple(row) for row in matrix)


def _pack_kernel_plan(self, plan: KernelPlan) -> PackedKernel:
    from .core import DEFAULT_PHASE_ORDER

    selector_names = tuple(sorted({key.selector for key in plan.opkey_to_meta.keys()}))
    proto_names = tuple(sorted(plan.proto_indices.keys()))
    op_names = tuple(
        f"{getattr(meta.model, '__name__', None) or getattr(meta.model, 'model_ref', None) or str(meta.model)}.{meta.alias}"
        for meta in plan.opmeta
    )

    proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
    selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
    op_to_id = {name: idx for idx, name in enumerate(op_names)}

    step_index: dict[int, int] = {}
    step_table: list[StepFn] = []
    step_labels: list[str] = []
    effect_ids: list[int] = []
    effect_payloads: list[tuple[int, ...]] = []

    segment_offsets: list[int] = []
    segment_lengths: list[int] = []
    segment_step_ids: list[int] = []
    segment_phases: list[str] = []
    segment_executor_kinds: list[str] = []

    op_segment_offsets: list[int] = []
    op_segment_lengths: list[int] = []
    op_to_segment_ids: list[int] = []

    for program_id, _meta in enumerate(plan.opmeta):
        chains = dict(plan.phase_chains.get(program_id, {}) or {})
        op_segment_offsets.append(len(op_to_segment_ids))
        seg_count = 0
        for phase in DEFAULT_PHASE_ORDER:
            steps = list(chains.get(phase, ()) or ())
            if not steps:
                continue

            seg_id = len(segment_offsets)
            segment_offsets.append(len(segment_step_ids))
            segment_lengths.append(len(steps))
            segment_phases.append(phase)

            kinds = {_classify_step_lowering(step, phase) for step in steps}
            if len(kinds) == 1 and LOWER_KIND_SYNC_EXTRACTABLE in kinds:
                segment_executor_kinds.append(LOWER_KIND_SYNC_EXTRACTABLE)
            elif LOWER_KIND_ASYNC_DIRECT in kinds:
                segment_executor_kinds.append(LOWER_KIND_ASYNC_DIRECT)
            else:
                segment_executor_kinds.append(LOWER_KIND_SPLIT_EXTRACTABLE)

            for step in steps:
                key = id(step)
                step_id = step_index.get(key)
                if step_id is None:
                    step_id = len(step_table)
                    step_index[key] = step_id
                    step_table.append(step)
                    step_labels.append(_label_step(step, phase))
                    effect_id, payload = _effect_descriptor_for_step(step)
                    effect_ids.append(effect_id)
                    effect_payloads.append(payload)
                segment_step_ids.append(step_id)

            op_to_segment_ids.append(seg_id)
            seg_count += 1
        op_segment_lengths.append(seg_count)

    route_to_program = self._build_route_matrix(
        proto_names=proto_names,
        selector_names=selector_names,
        opkey_to_meta=plan.opkey_to_meta,
    )

    packed = PackedKernel(
        proto_names=proto_names,
        selector_names=selector_names,
        op_names=op_names,
        proto_to_id=proto_to_id,
        selector_to_id=selector_to_id,
        op_to_id=op_to_id,
        route_to_program=route_to_program,
        segment_offsets=tuple(segment_offsets),
        segment_lengths=tuple(segment_lengths),
        segment_step_ids=tuple(segment_step_ids),
        segment_phases=tuple(segment_phases),
        segment_executor_kinds=tuple(segment_executor_kinds),
        op_segment_offsets=tuple(op_segment_offsets),
        op_segment_lengths=tuple(op_segment_lengths),
        op_to_segment_ids=tuple(op_to_segment_ids),
        step_table=tuple(step_table),
        step_labels=tuple(step_labels),
        numba_effect_ids=tuple(effect_ids),
        numba_effect_payloads=tuple(effect_payloads),
        executor_kind="python",
    )
    build_python_executor = getattr(self, "_build_python_packed_executor", None)
    build_numba_executor = getattr(self, "_build_numba_packed_executor", None)
    return replace(
        packed,
        executor=build_python_executor(packed)
        if callable(build_python_executor)
        else None,
        numba_executor=build_numba_executor(packed)
        if callable(build_numba_executor)
        else None,
    )


def _compile_bootstrap_plan(self, app: Any) -> Dict[str, List[StepFn]]:
    return self._build_ingress(app)
