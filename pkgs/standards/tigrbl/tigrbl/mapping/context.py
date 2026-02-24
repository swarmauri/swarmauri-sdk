from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from ..op import OpSpec

MappingKey = Tuple[str, str]


@dataclass(frozen=True)
class MappingContext:
    """Read-only snapshot of one deterministic mapping pass."""

    model: type
    router: Any | None
    only_keys: Optional[Set[MappingKey]]
    app_spec: Any | None = None
    router_specs: Mapping[str, Any] = field(default_factory=dict)
    op_specs: Mapping[str, Any] = field(default_factory=dict)
    model_specs: Mapping[str, Any] = field(default_factory=dict)
    alias_map: Mapping[str, str] = field(default_factory=dict)
    aliases: Mapping[str, FrozenSet[str]] = field(default_factory=dict)
    changed_keys: FrozenSet[MappingKey] = field(default_factory=frozenset)
    base_specs: Tuple[OpSpec, ...] = field(default_factory=tuple)
    ctx_specs: Tuple[OpSpec, ...] = field(default_factory=tuple)
    all_specs: Tuple[OpSpec, ...] = field(default_factory=tuple)
    visible_specs: Tuple[OpSpec, ...] = field(default_factory=tuple)
    merged_hooks: Dict[str, Dict[str, Sequence[Callable[..., Any]]]] = field(
        default_factory=dict
    )
    deps: Mapping[MappingKey, Tuple[Any, ...]] = field(default_factory=dict)
    secdeps: Mapping[MappingKey, Tuple[Any, ...]] = field(default_factory=dict)
    errors: Tuple[Exception, ...] = field(default_factory=tuple)
    bound_graph: Any | None = None

    def evolve(self, **changes: Any) -> "MappingContext":
        return replace(self, **changes)
