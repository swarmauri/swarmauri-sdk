# autoapi/v3/tables/_base.py
from __future__ import annotations

from typing import Any, Optional, Union, get_args, get_origin
from enum import Enum as PyEnum

from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from sqlalchemy import CheckConstraint, ForeignKey, MetaData
from sqlalchemy.types import Enum as SAEnum, String

# ──────────────────────────────────────────────────────────────────────────────
# Helpers – type inference & SA type instantiation
# ──────────────────────────────────────────────────────────────────────────────


def _unwrap_optional(t: Any) -> Any:
    """Optional[T] / Union[T, None]  →  T"""
    if get_origin(t) is Union:
        args = [a for a in get_args(t) if a is not type(None)]
        return args[0] if args else t
    return t


def _infer_py_type(cls, name: str, spec: Any) -> Optional[type]:
    """
    Prefer FieldSpec.py_type if provided; otherwise unwrap Mapped[...] / Optional[...]
    from the class' annotation to get the real Python type for the column.
    """
    fld = getattr(spec, "field", None)
    py = getattr(fld, "py_type", None)
    if isinstance(py, type):
        return py

    ann = getattr(cls, "__annotations__", {}).get(name)
    if ann is None:
        return None

    # Mapped[T] → T (then unwrap Optional)
    try:
        from sqlalchemy.orm import Mapped

        if get_origin(ann) is Mapped:
            inner = get_args(ann)[0]
            return _unwrap_optional(inner)
    except Exception:
        pass

    # Optional[T]/Union[T, None] → T
    return _unwrap_optional(ann)


def _instantiate_dtype(
    dtype: Any, py_type: Any, spec: Any, cls_name: str, col_name: str
):
    """
    Create a SQLAlchemy TypeEngine instance from either a type CLASS or an instance.
    - SAEnum: instantiate from the actual Enum class with a stable name
    - String: honor FieldSpec.constraints['max_length'] if present
    - UUID (PG): prefer as_uuid=True when available
    """
    # Already an instance? keep it.
    try:
        from sqlalchemy.sql.type_api import TypeEngine

        if isinstance(dtype, TypeEngine):
            return dtype
    except Exception:
        pass

    # SAEnum from a Python Enum class
    if dtype is SAEnum and isinstance(py_type, type) and issubclass(py_type, PyEnum):
        enum_name = f"{cls_name.lower()}_{col_name.lower()}"
        return SAEnum(py_type, name=enum_name, native_enum=True, validate_strings=True)

    # String – pick up max_length from FieldSpec
    if dtype is String:
        max_len = getattr(getattr(spec, "field", None), "constraints", {}).get(
            "max_length"
        )
        return String(max_len) if max_len else String()

    # PostgreSQL UUID (or similar) – try as_uuid=True first
    try:
        return dtype(as_uuid=True)  # e.g., PG UUID
    except TypeError:
        try:
            return dtype()
        except TypeError:
            # As a last resort, return the class; SQLA will raise clearly if unusable
            return dtype


def _materialize_colspecs_to_sqla(cls) -> None:
    """
    Replace ColumnSpec attributes with sqlalchemy.orm.mapped_column(...) BEFORE mapping.
    Keep the original specs in __autoapi_cols__ for downstream builders.
    """
    try:
        from autoapi.v3.specs.column_spec import ColumnSpec
    except Exception:
        return

    # Prefer explicit registry if present; otherwise scan the class dict.
    specs = getattr(cls, "__autoapi_cols__", None)
    if not isinstance(specs, dict) or not specs:
        specs = {k: v for k, v in cls.__dict__.items() if isinstance(v, ColumnSpec)}

    if not specs:
        return

    # Ensure downstream code can find the spec map
    setattr(cls, "__autoapi_cols__", dict(specs))

    for name, spec in specs.items():
        storage = getattr(spec, "storage", None)
        if not storage:
            # Virtual (wire-only) column – no DB column
            continue

        dtype = getattr(storage, "type_", None)
        if not dtype:
            # No SA dtype specified – cannot materialize
            continue

        py_type = _infer_py_type(cls, name, spec)
        dtype_inst = _instantiate_dtype(dtype, py_type, spec, cls.__name__, name)

        # Foreign key (if any)
        fk = getattr(storage, "fk", None)
        fk_arg = None
        if fk is not None:
            # ForeignKeySpec: target="table(col)", on_delete/on_update: "CASCADE"/...
            fk_arg = ForeignKey(fk.target, ondelete=fk.on_delete, onupdate=fk.on_update)

        check = getattr(storage, "check", None)
        args: list[Any] = []
        if fk_arg is not None:
            args.append(fk_arg)
        if check is not None:
            cname = f"ck_{cls.__name__.lower()}_{name}"
            args.append(CheckConstraint(check, name=cname))

        # Build mapped_column from StorageSpec flags
        mc = mapped_column(
            dtype_inst,
            *args,
            primary_key=getattr(storage, "primary_key", False),
            nullable=getattr(storage, "nullable", True),
            unique=getattr(storage, "unique", False),
            index=getattr(storage, "index", False),
            default=getattr(storage, "default", None),
            onupdate=getattr(storage, "onupdate", None),
            server_default=getattr(storage, "server_default", None),
            comment=getattr(storage, "comment", None),
            autoincrement=getattr(storage, "autoincrement", None),
            info={"autoapi": {"spec": spec}},
        )

        setattr(cls, name, mc)


# ──────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ──────────────────────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    def __init_subclass__(cls, **kw):
        # Allow redefining tables during tests or re-imports without SQLAlchemy
        # raising "Table ... is already defined".  Consumers can still override
        # ``__table_args__``; we just ensure ``extend_existing`` defaults to
        # ``True``.
        if not getattr(cls, "__abstract__", False):
            table_args = getattr(cls, "__table_args__", {})
            if isinstance(table_args, dict):
                table_args.setdefault("extend_existing", True)
            elif isinstance(table_args, tuple):
                if table_args and isinstance(table_args[-1], dict):
                    opts = dict(table_args[-1])
                    opts.setdefault("extend_existing", True)
                    table_args = (*table_args[:-1], opts)
                else:
                    table_args = (*table_args, {"extend_existing": True})
            else:
                table_args = {"extend_existing": True}
            setattr(cls, "__table_args__", table_args)

        # 1) BEFORE SQLAlchemy maps: turn ColumnSpecs into real mapped_column(...)
        _materialize_colspecs_to_sqla(cls)
        # 2) Let SQLAlchemy map the class (PK now exists)
        super().__init_subclass__(**kw)

        # 3) Seed model namespaces / index specs (ops/hooks/etc.) – idempotent
        try:
            from autoapi.v3.bindings import model as _model_bind

            _model_bind.bind(cls)
        except Exception:
            pass

        # 3) AUTO-BUILD CRUD schemas from ColumnSpecs so /docs has them
        try:
            from autoapi.v3.schema.build import build_for_model as _build_schemas

            _build_schemas(
                cls
            )  # attaches request/response models to the model/registry
        except Exception:
            # Surface during development if needed:
            # raise
            pass

    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(column_0_name)s_%(constraint_type)s",
        }
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()


__all__ = ["Base"]
