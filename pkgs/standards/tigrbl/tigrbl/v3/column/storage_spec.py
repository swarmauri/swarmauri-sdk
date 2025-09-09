# ---------------------------------------
# storage_spec.py (S)
# ---------------------------------------
from dataclasses import KW_ONLY, dataclass
from typing import Any, Literal, Union


@dataclass(frozen=True)
class StorageTransform:
    """Functions used to transform values on the way to and from the database."""

    to_stored: Union[callable, None] = (
        None  # (python, ctx) -> python persisted (e.g., hash/encrypt/normalize)
    )
    from_stored: Union[callable, None] = (
        None  # (python, ctx) -> python exposed (rare; only if you ever expose stored)
    )


@dataclass(frozen=True)
class ForeignKeySpec:
    """Lightweight description of a foreign key relationship."""

    target: str  # "tenant(id)" or fully-qualified
    on_delete: Literal["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"] = "RESTRICT"
    on_update: Literal["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"] = "RESTRICT"
    deferrable: bool = False
    initially_deferred: bool = False
    match: Literal["FULL", "PARTIAL", "SIMPLE"] = "SIMPLE"


@dataclass(frozen=True)
class StorageSpec:
    """Describe the database-level shape and behaviour of a column.

    The spec maps closely to SQLAlchemy's :class:`~sqlalchemy.Column` keyword
    arguments: ``type_`` and flags such as ``nullable`` or ``primary_key``
    define the table schema while ``default`` and ``onupdate`` represent ORM
    side defaults. ``server_default`` and ``refresh_on_return`` support
    database-generated values. Optional helpers provide value transforms,
    foreign keys, check constraints and comments.
    """

    # SQLAlchemy column shape (DDL/runtime)
    type_: Any | None = None
    _: KW_ONLY
    nullable: bool | None = None
    unique: bool = False
    index: bool = False
    primary_key: bool = False
    autoincrement: bool | None = None

    # ORM-side defaults (run in SQLAlchemy) – optional if you use API defaults/paired
    default: Any | None = None  # scalar or callable()
    onupdate: Any | None = None

    # DB-side defaults/generation (run in the database)
    server_default: Any | None = None  # e.g., func.now(), text("...")
    refresh_on_return: bool = False  # force refresh after flush when DB generated

    # Optional storage helpers
    transform: StorageTransform | None = None
    fk: ForeignKeySpec | None = None
    check: str | None = None
    comment: str | None = None
