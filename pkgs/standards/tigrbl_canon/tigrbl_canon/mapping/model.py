from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Set, Tuple

if TYPE_CHECKING:
    from tigrbl_core._spec import OpSpec
from .apply import apply
from .collect import collect
from .context import MappingKey
from .plan import plan


def bind(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> Tuple["OpSpec", ...]:
    context = collect(model, router=router, only_keys=only_keys)
    mapping_plan = plan(context)
    return tuple(apply(mapping_plan))


def rebind(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Optional[Set[MappingKey]] = None,
) -> Tuple["OpSpec", ...]:
    return bind(model, router=router, only_keys=changed_keys)


__all__ = ["bind", "rebind"]
