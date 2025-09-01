from __future__ import annotations
from typing import Iterable, Literal
from .table_config_provider import TableConfigProvider
from ..ops import OpSpec
from ..ops.canonical import (  # noqa: F401
    DEFAULT_CANON_VERBS,
    should_wire_canonical,
)


class OpConfigProvider(TableConfigProvider):
    __autoapi_ops__: Iterable[OpSpec] = ()

    # Default canonical verbs wiring policy
    __autoapi_defaults_mode__: Literal["all", "none", "some"] = "all"
    __autoapi_defaults_include__: set[str] = set()
    __autoapi_defaults_exclude__: set[str] = set()
