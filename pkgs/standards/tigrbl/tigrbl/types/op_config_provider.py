from __future__ import annotations
from typing import Iterable, Literal
from .table_config_provider import TableConfigProvider
from ..op import OpSpec
from ..op.canonical import (  # noqa: F401
    DEFAULT_CANON_VERBS,
    should_wire_canonical,
)


class OpConfigProvider(TableConfigProvider):
    __tigrbl_ops__: Iterable[OpSpec] = ()

    # Default canonical verbs wiring policy
    __tigrbl_defaults_mode__: Literal["all", "none", "some"] = "all"
    __tigrbl_defaults_include__: set[str] = set()
    __tigrbl_defaults_exclude__: set[str] = set()
