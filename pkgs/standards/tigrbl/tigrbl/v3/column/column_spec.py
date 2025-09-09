from __future__ import annotations

from typing import Any, Callable, Optional

from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


class ColumnSpec:
    """Configuration container for column construction."""

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
