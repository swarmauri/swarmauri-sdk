# autoapi/v2/types/skip_persist_provider.py
from __future__ import annotations

from typing import Any, Final, FrozenSet, Iterable, Optional, Sequence, Set, Type

try:
    # v2 base, adjust the import path if yours differs
    from .table_config_provider import TableConfigProvider
except Exception:  # pragma: no cover - keeps this file importable in isolation
    class TableConfigProvider:  # type: ignore
        """Fallback stub if the base isn't importable during tooling."""

SKIP_PERSIST_KEY: Final[str] = "__autoapi_skip_persist__"


class SkipPersistProvider(TableConfigProvider):
    """
    Table-level config provider enabling *ephemeral* (no-DB) handling per verb.

    Models can declare on the class:

        # Skip everything → fully ephemeral
        __autoapi_skip_persist__ = {"*"}

        # Skip only specific ops
        __autoapi_skip_persist__ = {"create", "update"}

        # Bool alias for wildcard
        __autoapi_skip_persist__ = True

        # Or compute dynamically
        @classmethod
        def __autoapi_skip_persist__(cls):
            return {"create"} if cls.__name__.endswith("Handshake") else set()

    Notes
    -----
    - The value may be a bool, str, iterable of str, set, or a callable returning
      any of the above. "*" means "all available ops".
    - All verbs are lower-cased during normalization.
    - Integration points typically call:
         - SkipPersistProvider.resolve_for_ops(Model, available_ops)
         - SkipPersistProvider.should_skip(Model, verb, available_ops)
    """

    CONFIG_KEY: Final[str] = SKIP_PERSIST_KEY

    # ----------------------------
    # Public helpers (used by router/cores)
    # ----------------------------
    @classmethod
    def is_configured(cls, model: Type[Any]) -> bool:
        return hasattr(model, cls.CONFIG_KEY)

    @classmethod
    def raw_value(cls, model: Type[Any]) -> Any:
        if not cls.is_configured(model):
            return None
        val = getattr(model, cls.CONFIG_KEY)
        return val(model) if callable(val) else val

    @classmethod
    def normalized(cls, model: Type[Any]) -> FrozenSet[str]:
        """Return the raw config normalized to a frozenset of lower-cased verbs,
        possibly containing the wildcard '*'. Empty set means 'do not skip'."""
        val = cls.raw_value(model)

        # Alias True → {"*"}
        if val is True:
            return frozenset({"*"})

        # Single string → treat as one token (commas are not special here)
        if isinstance(val, str):
            return frozenset({val.strip().lower()}) if val.strip() else frozenset()

        # Iterable of strings (list/tuple/set/frozenset/etc.)
        if isinstance(val, Iterable):
            out: Set[str] = set()
            for item in val:
                if item is True:
                    out.add("*")
                elif isinstance(item, str):
                    s = item.strip().lower()
                    if s:
                        out.add(s)
                else:
                    raise TypeError(
                        f"{cls.__name__}: unsupported item in iterable config: {type(item)!r}"
                    )
            return frozenset(out)

        # None or False → not configured
        if val in (None, False):
            return frozenset()

        raise TypeError(
            f"{cls.__name__}: unsupported config type {type(val)!r} on {model!r}"
        )

    @classmethod
    def resolve_for_ops(
        cls,
        model: Type[Any],
        available_ops: Iterable[str],
    ) -> FrozenSet[str]:
        """
        Expand '*' against the provided available ops and return the final skip set.
        """
        declared = cls.normalized(model)
        if not declared:
            return frozenset()

        if "*" in declared:
            return frozenset(op.lower() for op in available_ops)

        avail = {op.lower() for op in available_ops}
        return frozenset(op for op in declared if op in avail)

    @classmethod
    def should_skip(
        cls,
        model: Type[Any],
        verb: str,
        available_ops: Optional[Iterable[str]] = None,
    ) -> bool:
        """
        Fast check for a single verb. If available_ops is provided, '*' will be
        considered a match; otherwise '*' always implies True.
        """
        declared = cls.normalized(model)
        if not declared:
            return False

        v = verb.lower()
        if "*" in declared:
            return True if available_ops is None else v in {
                op.lower() for op in available_ops
            }

        return v in declared


__all__ = ["SkipPersistProvider", "SKIP_PERSIST_KEY"]
