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
