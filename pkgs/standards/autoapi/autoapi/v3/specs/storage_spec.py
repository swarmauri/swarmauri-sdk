# ---------------------------------------
# storage_spec.py (S)
# ---------------------------------------
from dataclasses import dataclass
from typing import Any, Literal, Union


@dataclass(frozen=True)
class StorageTransform:
    to_stored: Union[callable, None] = (
        None  # (python, ctx) -> python persisted (e.g., hash/encrypt/normalize)
    )
    from_stored: Union[callable, None] = (
        None  # (python, ctx) -> python exposed (rare; only if you ever expose stored)
    )


@dataclass(frozen=True)
class ForeignKeySpec:
    target: str  # "tenant(id)" or fully-qualified
    on_delete: Literal["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"] = "RESTRICT"
    on_update: Literal["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"] = "RESTRICT"
    deferrable: bool = False
    initially_deferred: bool = False
    match: Literal["FULL", "PARTIAL", "SIMPLE"] = "SIMPLE"


@dataclass(frozen=True)
class StorageSpec:
    # SQLAlchemy column shape (DDL/runtime)
    type_: Any | None = None
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
