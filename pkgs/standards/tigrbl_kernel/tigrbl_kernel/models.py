from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Mapping, Tuple

try:
    from tigrbl_typing.phases import MAINLINE_PHASES, ERROR_PHASES, phase_info
except Exception:  # pragma: no cover - compatibility fallback
    MAINLINE_PHASES = ()
    ERROR_PHASES = ()
    phase_info = None


StepFn = Callable[..., Any]


def _label_callable(fn: Any) -> str:
    name = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    module = getattr(fn, "__module__", None)
    return f"{module}.{name}" if module else name


def _label_step(step: Any, phase: str) -> str:
    label = getattr(step, "__tigrbl_label", None)
    if isinstance(label, str) and "@" in label:
        return label
    module = getattr(step, "__module__", "") or ""
    name = getattr(step, "__name__", "") or ""
    if (
        module.startswith("tigrbl_ops_oltp.crud")
        or module.startswith("tigrbl_core.core.crud")
        and name
    ):
        return f"hook:wire:tigrbl:core:crud:ops:{name}@{phase}"
    return f"hook:wire:{_label_callable(step).replace('.', ':')}@{phase}"


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


@dataclass(frozen=True, slots=True)
class OpKey:
    proto: str
    selector: str


@dataclass(frozen=True, slots=True)
class OpMeta:
    model: type
    alias: str
    target: str


@dataclass(frozen=True, slots=True)
class CompiledPhase:
    name: str
    stage_in: object | None
    stage_out: object | None
    in_tx: bool = False
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class PackedSegment:
    id: int
    phase: str
    offset: int
    length: int
    label: str
    executor_kind: str = "python"


@dataclass(frozen=True, slots=True)
class PackedKernel:
    proto_names: tuple[str, ...] = ()
    selector_names: tuple[str, ...] = ()
    op_names: tuple[str, ...] = ()

    proto_to_id: Mapping[str, int] = field(default_factory=dict)
    selector_to_id: Mapping[str, int] = field(default_factory=dict)
    op_to_id: Mapping[str, int] = field(default_factory=dict)

    route_to_program: Any = None

    segment_offsets: tuple[int, ...] = ()
    segment_lengths: tuple[int, ...] = ()
    segment_step_ids: tuple[int, ...] = ()
    segment_phases: tuple[str, ...] = ()
    segment_executor_kinds: tuple[str, ...] = ()

    op_segment_offsets: tuple[int, ...] = ()
    op_segment_lengths: tuple[int, ...] = ()
    op_to_segment_ids: tuple[int, ...] = ()

    step_table: tuple[StepFn, ...] = ()
    step_labels: tuple[str, ...] = ()

    numba_effect_ids: tuple[int, ...] = ()
    numba_effect_payloads: tuple[tuple[int, ...], ...] = ()

    ingress_program_id: int = -1
    egress_ok_program_id: int = -1
    egress_err_program_id: int = -1

    executor_kind: str = "python"
    executor: Callable[..., Any] | None = None
    numba_executor: Callable[..., Any] | None = None


@dataclass(frozen=True, slots=True)
class KernelPlan:
    proto_indices: Mapping[str, Any] = field(default_factory=dict)
    opmeta: tuple[OpMeta, ...] = ()
    opkey_to_meta: Mapping[OpKey, int] = field(default_factory=dict)
    ingress_chain: Mapping[str, list[StepFn]] = field(default_factory=dict)
    phase_chains: Mapping[int, Mapping[str, list[StepFn]]] = field(default_factory=dict)
    egress_chain: Mapping[str, list[StepFn]] = field(default_factory=dict)
    phases: Mapping[str, CompiledPhase] = field(default_factory=dict)
    mainline_phases: tuple[str, ...] = ()
    error_phases: tuple[str, ...] = ()
    packed: PackedKernel | None = None
    _appspec_mapping: Dict[str, Dict[str, list[str]]] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )

    def _normalize_mappings(self) -> Dict[str, Dict[str, list[str]]]:
        if self._appspec_mapping:
            return self._appspec_mapping

        phase_order = self.mainline_phases or tuple(self.phases.keys())
        if not phase_order:
            phase_order = tuple(self.ingress_chain.keys()) or tuple()

        normalized: Dict[str, Dict[str, list[str]]] = {}
        for meta_index, meta in enumerate(self.opmeta):
            table_name = getattr(meta.model, "__name__", str(meta.model))
            labels: list[str] = []
            chains = self.phase_chains.get(meta_index, {})
            for phase in phase_order:
                phase_steps = chains.get(phase, ())
                for step in phase_steps or ():
                    labels.append(_label_step(step, phase))

            seen, deduped = set(), []
            for label in labels:
                if ":hook:wire:" in label:
                    if label in seen:
                        continue
                    seen.add(label)
                deduped.append(label)

            normalized.setdefault(table_name, {})[meta.alias] = deduped

        self._appspec_mapping.update(normalized)
        return self._appspec_mapping

    def __getitem__(self, key: str) -> Dict[str, list[str]]:
        return self._normalize_mappings()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._normalize_mappings())

    def __len__(self) -> int:
        return len(self._normalize_mappings())

    def get(
        self, key: str, default: Dict[str, list[str]] | None = None
    ) -> Dict[str, list[str]] | None:
        return self._normalize_mappings().get(key, default)

    def items(self):
        return self._normalize_mappings().items()

    def keys(self):
        return self._normalize_mappings().keys()

    def values(self):
        return self._normalize_mappings().values()
