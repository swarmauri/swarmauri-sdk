from __future__ import annotations

from typing import Mapping

from tigrbl_core._spec.op_spec import OpSpec


def apply_alias(verb: str, alias_map: Mapping[str, str]) -> str:
    """Deprecated compatibility shim; use :meth:`OpSpec.apply_alias`."""

    return OpSpec.apply_alias(verb, alias_map)


def collect(table: type) -> tuple[OpSpec, ...]:
    """Deprecated compatibility shim; use :meth:`OpSpec.collect`."""

    return OpSpec.collect(table)


__all__ = ["apply_alias", "collect"]
