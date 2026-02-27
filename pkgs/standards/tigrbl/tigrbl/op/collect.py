from __future__ import annotations

from typing import Dict

from .._spec.op_spec import OpSpec


def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Deprecated compatibility shim; use :meth:`OpSpec.apply_alias`."""

    return OpSpec.apply_alias(verb, alias_map)


__all__ = ["apply_alias"]
