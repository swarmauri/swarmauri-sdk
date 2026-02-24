from __future__ import annotations

from typing import Any, Callable, Optional

from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


class ColumnSpec:
    """Aggregate configuration for a model attribute.

    A :class:`ColumnSpec` brings together the three lower-level specs used by
    Tigrbl's declarative column system:

    - ``storage`` (:class:`~tigrbl.column.storage_spec.StorageSpec`) controls
      how the value is persisted in the database.
    - ``field`` (:class:`~tigrbl.column.field_spec.FieldSpec`) describes the
      Python type and any schema metadata.
    - ``io`` (:class:`~tigrbl.column.io_spec.IOSpec`) governs inbound and
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
