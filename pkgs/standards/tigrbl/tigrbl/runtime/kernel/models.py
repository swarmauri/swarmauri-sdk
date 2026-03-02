from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Mapping, Tuple


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
    if module.startswith("tigrbl.core.crud") and name:
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
class KernelPlan:
    proto_indices: Mapping[str, Any] = field(default_factory=dict)
    opmeta: tuple[OpMeta, ...] = ()
    opkey_to_meta: Mapping[OpKey, int] = field(default_factory=dict)
    ingress_chain: Mapping[str, list[Callable[..., Any]]] = field(default_factory=dict)
    phase_chains: Mapping[int, Mapping[str, list[Callable[..., Any]]]] = field(
        default_factory=dict
    )
    egress_chain: Mapping[str, list[Callable[..., Any]]] = field(default_factory=dict)
    _appspec_mapping: Dict[str, Dict[str, list[str]]] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )

    def _normalize_mappings(self) -> Dict[str, Dict[str, list[str]]]:
        if self._appspec_mapping:
            return self._appspec_mapping

        from ...runtime import events as _ev

        normalized: Dict[str, Dict[str, list[str]]] = {}
        for meta_index, meta in enumerate(self.opmeta):
            table_name = getattr(meta.model, "__name__", str(meta.model))
            labels: list[str] = []
            chains = self.phase_chains.get(meta_index, {})
            for phase in _ev.PHASES:
                phase_steps = chains.get(phase, ())
                for step in phase_steps or ():
                    labels.append(f"{phase}:{_label_step(step, phase)}")

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
