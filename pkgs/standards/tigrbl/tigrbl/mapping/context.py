from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Set, Tuple

from ..op import OpSpec

MappingKey = Tuple[str, str]


@dataclass(frozen=True)
class MappingContext:
    """Immutable-ish snapshot collected once per binding pass."""

    model: type
    router: Any | None
    only_keys: Optional[Set[MappingKey]]
    alias_map: Mapping[str, str]
    base_specs: Tuple[OpSpec, ...]
    ctx_specs: Tuple[OpSpec, ...]
    changed_keys: Set[MappingKey] = field(default_factory=set)


@dataclass(frozen=True)
class MappingPlan:
    """Compilation-ready mapping plan produced from MappingContext."""

    model: type
    router: Any | None
    only_keys: Optional[Set[MappingKey]]
    alias_map: Mapping[str, str]
    all_specs: Tuple[OpSpec, ...]
    visible_specs: Tuple[OpSpec, ...]
    merged_hooks: Dict[str, Dict[str, List[Callable[..., Any]]]]
