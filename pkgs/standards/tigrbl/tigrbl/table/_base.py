# tigrbl/tigrbl/v3/table/_base.py
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
        from ..types import Mapped

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
    Keep the original specs in __tigrbl_cols__ for downstream builders.
    """
    try:
        from tigrbl.column.column_spec import ColumnSpec
    except Exception:
        return

    # Prefer explicit registry if present; otherwise collect specs from the
    # entire MRO so mixins contribute their ColumnSpec definitions.
    specs: dict[str, ColumnSpec] = {}
    for base in reversed(cls.__mro__):
        base_specs = getattr(base, "__tigrbl_cols__", None)
        if isinstance(base_specs, dict) and base_specs:
            specs.update(base_specs)
            continue
        for name, attr in getattr(base, "__dict__", {}).items():
            if isinstance(attr, ColumnSpec):
                specs.setdefault(name, attr)

    if not specs:
        return

    # Ensure downstream code can find the spec map
    setattr(cls, "__tigrbl_cols__", dict(specs))

    for name, spec in specs.items():
        storage = getattr(spec, "storage", None)
        if not storage:
            # Virtual (wire-only) column.
            # If the attribute is a Column descriptor (i.e. declared via vcol/acol),
            # materialize a SQLAlchemy mapped column using the inferred Python type
            # so the ORM instruments it and the table metadata contains the column.
            try:
                from tigrbl.column._column import Column as _TigrblColumn
            except Exception:
                _TigrblColumn = None  # type: ignore

            orig_attr = getattr(cls, name, None)
            if _TigrblColumn is not None and isinstance(orig_attr, _TigrblColumn):
                try:
                    # Infer a Python type, then pick a reasonable SQLAlchemy dtype.
                    py_type = _infer_py_type(cls, name, spec)
                    # Plan an SA type from the python type and field constraints
                    try:
                        from tigrbl.column.infer.core import infer as _infer_sa

                        plan = _infer_sa(py_type)
                        # Resolve SA type class from exported types module when possible
                        from tigrbl import types as _types

                        dtype_cls = getattr(_types, plan.sa.name, None)
                    except Exception:
                        dtype_cls = None

                    # Fallbacks if inference is unavailable
                    if dtype_cls is None:
                        try:
                            from sqlalchemy.types import String as _SAString

                            dtype_cls = _SAString
                        except Exception:
                            dtype_cls = None

                    if dtype_cls is not None:
                        dtype_inst = _instantiate_dtype(
                            dtype_cls, py_type, spec, cls.__name__, name
                        )
                        mc = mapped_column(dtype_inst, nullable=True)
                        setattr(cls, name, mc)
                except Exception:
                    # Best-effort only; leave attribute as-is if anything fails
                    pass
            # If it is a bare ColumnSpec attribute (e.g., declared on Table for namespacing),
            # do not delete or materialize it; leave it available via cls.columns and attribute.
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
        )

        setattr(cls, name, mc)


# ──────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ──────────────────────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    __allow_unmapped__ = True

    def __init_subclass__(cls, **kw):
        # 0) Remove any previously registered class with the same name.
        try:
            reg = Base.registry._class_registry
            keys = [cls.__name__, f"{cls.__module__}.{cls.__name__}"]
            existing = next((reg.get(k) for k in keys if reg.get(k) is not None), None)
            if existing is not None:
                try:
                    Base.registry._dispose_cls(existing)
                except Exception:
                    pass
                for k in keys:
                    reg.pop(k, None)
        except Exception:
            pass

        # 1) BEFORE SQLAlchemy maps: turn ColumnSpecs into real mapped_column(...)
        _materialize_colspecs_to_sqla(cls)

        # 2) Let SQLAlchemy map the class (PK now exists)
        super().__init_subclass__(**kw)

        # 3) Seed model namespaces / index specs (ops/hooks/etc.) – idempotent
        try:
            from tigrbl.bindings import model as _model_bind

            _model_bind.bind(cls)
        except Exception:
            pass

        # 3) AUTO-BUILD CRUD schemas from ColumnSpecs so /docs has them
        try:
            from tigrbl.schema.build import build_for_model as _build_schemas

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

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access to model attributes."""
        return getattr(self, key)


__all__ = ["Base"]
