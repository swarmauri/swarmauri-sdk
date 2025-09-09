"""Support for request/response extras in schema building."""

from __future__ import annotations

import logging
from typing import Any, Dict, Set, Tuple

from pydantic import Field

from ...config.constants import (
    TIGRBL_REQUEST_EXTRAS_ATTR,
    TIGRBL_RESPONSE_EXTRAS_ATTR,
)
from .helpers import _add_field

logger = logging.getLogger(__name__)


def _merge_request_extras(
    orm_cls: type,
    verb: str,
    fields: Dict[str, Tuple[type, Field]],
    *,
    include: Set[str] | None,
    exclude: Set[str] | None,
) -> None:
    """Merge request-only virtual fields into the schema."""
    buckets = getattr(orm_cls, TIGRBL_REQUEST_EXTRAS_ATTR, None)
    if not buckets:
        return
    if verb not in {"create", "update", "replace", "delete"}:
        return

    for bucket in (buckets.get("*", {}), buckets.get(verb, {})):
        for name, spec in (bucket or {}).items():
            if include and name not in include:
                continue
            if exclude and name in exclude:
                continue
            if isinstance(spec, tuple) and len(spec) == 2:
                py_t, fld = spec
            else:
                py_t, fld = (spec or Any), Field(None)
            _add_field(fields, name=name, py_t=py_t, field=fld)
            logger.debug(
                "schema: added request-extra field %s (verb=%s, type=%r)",
                name,
                verb,
                py_t,
            )


def _merge_response_extras(
    orm_cls: type,
    verb: str,
    fields: Dict[str, Tuple[type, Field]],
    *,
    include: Set[str] | None,
    exclude: Set[str] | None,
) -> None:
    """Merge response-only virtual fields into the schema."""
    buckets = getattr(orm_cls, TIGRBL_RESPONSE_EXTRAS_ATTR, None)
    if not buckets:
        return

    for bucket in (buckets.get("*", {}), buckets.get(verb, {})):
        for name, spec in (bucket or {}).items():
            if include and name not in include:
                continue
            if exclude and name in exclude:
                continue
            if isinstance(spec, tuple) and len(spec) == 2:
                py_t, fld = spec
            else:
                py_t, fld = (spec or Any), Field(None)
            _add_field(fields, name=name, py_t=py_t, field=fld)
            logger.debug(
                "schema: added response-extra field %s (verb=%s, type=%r)",
                name,
                verb,
                py_t,
            )


__all__ = ["_merge_request_extras", "_merge_response_extras"]
