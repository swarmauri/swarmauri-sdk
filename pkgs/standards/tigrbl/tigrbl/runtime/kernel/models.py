from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Tuple


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

    def _legacy_payload(self) -> dict[str, dict[str, list[str]]]:
        payload: dict[str, dict[str, list[str]]] = {}
        for index, meta in enumerate(self.opmeta):
            chains = self.phase_chains.get(index, {})
            sequence: list[str] = []
            for phase, steps in chains.items():
                for step in steps or ():
                    label = getattr(step, "__tigrbl_label", None)
                    if isinstance(label, str):
                        entry = label
                    else:
                        name = getattr(
                            step, "__qualname__", getattr(step, "__name__", repr(step))
                        )
                        module = getattr(step, "__module__", None)
                        subject = f"{module}.{name}" if module else name
                        entry = f"hook:wire:{subject.replace('.', ':')}@{phase}"
                    sequence.append(f"{phase}:{entry}")
            model_name = getattr(meta.model, "__name__", "Model")
            payload.setdefault(model_name, {})[meta.alias] = sequence
        return payload

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str) and hasattr(self, key):
            return getattr(self, key)
        return self._legacy_payload()[key]
