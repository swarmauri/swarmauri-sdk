from __future__ import annotations

from ...config.constants import BULK_VERBS
from ...types import declarative_mixin


@declarative_mixin
class BulkCapable:
    __tigrbl_defaults_mode__: str = "all"
    __tigrbl_defaults_include__: set[str] = {
        v for v in BULK_VERBS if v not in {"bulk_replace", "bulk_merge"}
    }
    __tigrbl_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__tigrbl_defaults_include__", set()))
        inc.update(BulkCapable.__tigrbl_defaults_include__)
        cls.__tigrbl_defaults_include__ = inc

        exc = set(getattr(cls, "__tigrbl_defaults_exclude__", set()))
        exc.update(BulkCapable.__tigrbl_defaults_exclude__)
        cls.__tigrbl_defaults_exclude__ = exc


@declarative_mixin
class Replaceable:
    __tigrbl_defaults_mode__: str = "all"
    __tigrbl_defaults_include__: set[str] = {"replace", "bulk_replace"}
    __tigrbl_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__tigrbl_defaults_include__", set()))
        inc.update(Replaceable.__tigrbl_defaults_include__)
        cls.__tigrbl_defaults_include__ = inc


@declarative_mixin
class Mergeable:
    __tigrbl_defaults_mode__: str = "all"
    __tigrbl_defaults_include__: set[str] = {"merge", "bulk_merge"}
    __tigrbl_defaults_exclude__: set[str] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        inc = set(getattr(cls, "__tigrbl_defaults_include__", set()))
        inc.update(Mergeable.__tigrbl_defaults_include__)
        cls.__tigrbl_defaults_include__ = inc


@declarative_mixin
class Streamable:
    pass


__all__ = ["BulkCapable", "Replaceable", "Mergeable", "Streamable"]
