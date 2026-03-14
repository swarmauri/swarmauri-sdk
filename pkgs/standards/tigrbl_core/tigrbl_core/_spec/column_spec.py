from __future__ import annotations

import logging
from functools import lru_cache
from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional

from .._spec.field_spec import FieldSpec as F
from .._spec.io_spec import IOSpec as IO
from .._spec.storage_spec import StorageSpec as S
from .serde import SerdeMixin

logger = logging.getLogger("uvicorn")


class ColumnSpec(SerdeMixin):
    """Aggregate configuration for a model attribute.

    A :class:`ColumnSpec` brings together the three lower-level specs used by
    Tigrbl's declarative column system:

    - ``storage`` (:class:`~tigrbl._spec.storage_spec.StorageSpec`) controls
      how the value is persisted in the database.
    - ``field`` (:class:`~tigrbl._spec.field_spec.FieldSpec`) describes the
      Python type and any schema metadata.
    - ``io`` (:class:`~tigrbl._spec.io_spec.IOSpec`) governs inbound and
      outbound API exposure.

    Optional ``default_factory`` and ``read_producer`` callables allow for
    programmatic defaults and virtual read-time values respectively.
    """

    def __init__(
        self,
        *,
        storage: S | None,
        field: F | None = None,
        io: IO | None = None,
        default_factory: Optional[Callable[[dict], Any]] = None,
        read_producer: Optional[Callable[[object, dict], Any]] = None,
    ) -> None:
        self.storage = storage
        self.field = field if field is not None else F()
        self.io = io if io is not None else IO()
        self.default_factory = default_factory
        self.read_producer = read_producer

    # Default inbound/outbound verbs for columns lacking an explicit ColumnSpec.
    #
    # Without this, plain SQLAlchemy ``Column`` definitions are omitted from the
    # collected spec map, causing downstream components to treat their values as
    # unknown. By seeding such columns with a permissive IO spec we ensure they
    # participate in canonical CRUD operations just like columns defined via
    # ``acol``.
    _DEFAULT_IO = IO(
        in_verbs=("create", "update", "replace"),
        out_verbs=("read", "list"),
        mutable_verbs=("create", "update", "replace"),
    )

    @staticmethod
    def _model_label(model: object) -> str:
        return str(
            getattr(model, "__name__", None)
            or getattr(model, "name", None)
            or type(model).__name__
        )

    @staticmethod
    def _coerce_columns_iterable(columns: object) -> tuple[object, ...]:
        """Normalize model/table column containers to an iterable tuple.

        Some table classes expose ``columns`` as a ``SimpleNamespace`` of
        ``ColumnSpec`` objects for convenience. Runtime collectors should treat
        that namespace as a mapping and iterate over its values rather than
        trying to iterate the namespace object directly.
        """

        if isinstance(columns, SimpleNamespace):
            return tuple(columns.__dict__.values())
        if isinstance(columns, dict):
            return tuple(columns.values())
        try:
            return tuple(columns)  # type: ignore[arg-type]
        except TypeError:
            return ()

    @staticmethod
    @lru_cache(maxsize=None)
    def _mro_collect_columns_cached(
        model: object, _cache_bust: int
    ) -> Dict[str, "ColumnSpec"]:
        """Collect ColumnSpecs declared on *model* and all mixins.

        Iterates across the model's MRO so that mixin-defined columns are
        included in the resulting mapping. Later definitions take precedence
        over earlier ones in the MRO. Any table-backed columns lacking a spec
        are populated with a default ColumnSpec so they participate in opviews
        and schema generation.
        """
        logger.info("Collecting columns for %s", ColumnSpec._model_label(model))
        out: Dict[str, ColumnSpec] = {}
        mro = getattr(model, "__mro__", ()) or ()
        for base in reversed(mro):
            mapping = getattr(base, "__tigrbl_colspecs__", None)
            if isinstance(mapping, dict):
                out.update(mapping)
            mapping = getattr(base, "__tigrbl_cols__", None)
            if isinstance(mapping, dict):
                out.update(mapping)

        cols = None
        table = getattr(model, "__table__", None)
        if table is not None:
            cols = getattr(table, "columns", None)
        elif hasattr(model, "columns"):
            cols = getattr(model, "columns", None)

        if cols is not None:
            for col in ColumnSpec._coerce_columns_iterable(cols):
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if not isinstance(name, str):
                    continue
                out.setdefault(name, ColumnSpec(storage=S(), io=ColumnSpec._DEFAULT_IO))

        logger.info(
            "Collected %d columns for %s", len(out), ColumnSpec._model_label(model)
        )
        return out

    @classmethod
    def collect(
        cls, model: object, *, _cache_bust: int | None = None
    ) -> Dict[str, "ColumnSpec"]:
        """Collect ColumnSpecs for *model* with topology-aware cache busting."""

        if _cache_bust is None:
            table = getattr(model, "__table__", None)
            cols = getattr(table, "columns", None) if table is not None else None
            col_count = (
                len(cls._coerce_columns_iterable(cols)) if cols is not None else 0
            )
            _cache_bust = hash(
                (
                    id(getattr(model, "__tigrbl_colspecs__", None)),
                    id(getattr(model, "__tigrbl_cols__", None)),
                    id(table),
                    col_count,
                )
            )
        return cls._mro_collect_columns_cached(model, _cache_bust)

    @classmethod
    def mro_collect_columns(
        cls, model: object, *, _cache_bust: int | None = None
    ) -> Dict[str, "ColumnSpec"]:
        """Backward-compatible alias for :meth:`collect`."""

        return cls.collect(model, _cache_bust=_cache_bust)


def mro_collect_columns(
    model: object, *, _cache_bust: int | None = None
) -> Dict[str, ColumnSpec]:
    return ColumnSpec.collect(model, _cache_bust=_cache_bust)


mro_collect_columns.cache_clear = ColumnSpec._mro_collect_columns_cached.cache_clear

__all__ = ["ColumnSpec", "mro_collect_columns"]
