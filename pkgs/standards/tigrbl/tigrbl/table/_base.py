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


def _materialize_colspecs_to_sqla(cls, *, map_columns: bool = True) -> None:
    """
    Replace ColumnSpec attributes with sqlalchemy.orm.mapped_column(...) BEFORE mapping.
    Keep the original specs in __tigrbl_cols__ for downstream builders.
    """
    try:
        from tigrbl.column.column_spec import ColumnSpec
    except Exception:
        return
    try:
        from sqlalchemy.orm import InstrumentedAttribute, MappedColumn
    except Exception:  # pragma: no cover - defensive for minimal SQLA envs
        InstrumentedAttribute = None
        MappedColumn = None

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

    if map_columns:
        for name, spec in specs.items():
            storage = getattr(spec, "storage", None)
            if not storage:
                # Virtual (wire-only) column – ensure SQLAlchemy ignores it.
                if MappedColumn is not None and isinstance(spec, MappedColumn):
                    annotations = getattr(cls, "__annotations__", {}) or {}
                    if name not in annotations:
                        replacement = ColumnSpec(
                            storage=None,
                            field=getattr(spec, "field", None),
                            io=getattr(spec, "io", None),
                            default_factory=getattr(spec, "default_factory", None),
                            read_producer=getattr(spec, "read_producer", None),
                        )
                        setattr(cls, name, replacement)
                        specs[name] = replacement
                continue
            existing_attr = getattr(cls, name, None)
            if InstrumentedAttribute is not None and isinstance(
                existing_attr, InstrumentedAttribute
            ):
                # Column already mapped on a base class; avoid duplicating columns
                # that trigger SQLAlchemy implicit combination warnings.
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
                fk_arg = ForeignKey(
                    fk.target, ondelete=fk.on_delete, onupdate=fk.on_update
                )

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

    # Ensure downstream code can find the spec map
    setattr(cls, "__tigrbl_cols__", dict(specs))


def _ensure_instrumented_attr_accessors() -> None:
    """Expose ColumnSpec metadata on SQLAlchemy InstrumentedAttribute objects."""
    try:
        from sqlalchemy.orm.attributes import InstrumentedAttribute
    except Exception:  # pragma: no cover - defensive for minimal SQLA envs
        return

    if not hasattr(InstrumentedAttribute, "storage"):

        def _storage(self):  # type: ignore[no-untyped-def]
            spec = getattr(self.class_, "__tigrbl_cols__", {}).get(self.key)
            return getattr(spec, "storage", None)

        InstrumentedAttribute.storage = property(_storage)  # type: ignore[attr-defined]

    if not hasattr(InstrumentedAttribute, "field"):

        def _field(self):  # type: ignore[no-untyped-def]
            spec = getattr(self.class_, "__tigrbl_cols__", {}).get(self.key)
            return getattr(spec, "field", None)

        InstrumentedAttribute.field = property(_field)  # type: ignore[attr-defined]

    if not hasattr(InstrumentedAttribute, "io"):

        def _io(self):  # type: ignore[no-untyped-def]
            spec = getattr(self.class_, "__tigrbl_cols__", {}).get(self.key)
            return getattr(spec, "io", None)

        InstrumentedAttribute.io = property(_io)  # type: ignore[attr-defined]

    if not hasattr(InstrumentedAttribute, "default_factory"):

        def _default_factory(self):  # type: ignore[no-untyped-def]
            spec = getattr(self.class_, "__tigrbl_cols__", {}).get(self.key)
            return getattr(spec, "default_factory", None)

        InstrumentedAttribute.default_factory = property(_default_factory)  # type: ignore[attr-defined]

    if not hasattr(InstrumentedAttribute, "read_producer"):

        def _read_producer(self):  # type: ignore[no-untyped-def]
            spec = getattr(self.class_, "__tigrbl_cols__", {}).get(self.key)
            return getattr(spec, "read_producer", None)

        InstrumentedAttribute.read_producer = property(_read_producer)  # type: ignore[attr-defined]


# ──────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ──────────────────────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    __allow_unmapped__ = True

    def __init_subclass__(cls, **kw):
        # 0) Remove any previously registered class with the same module path.
        try:
            reg = Base.registry._class_registry
            name = cls.__name__
            existing = reg.get(name)
            if existing is not None:
                try:
                    Base.registry._dispose_cls(existing)
                except Exception:
                    pass
                reg.pop(name, None)
            module_reg = reg.get("_sa_module_registry")
            if module_reg is not None:
                marker = module_reg
                for part in cls.__module__.split("."):
                    contents = getattr(marker, "contents", None)
                    if not isinstance(contents, dict) or part not in contents:
                        marker = None
                        break
                    marker = contents.get(part)
                if marker is not None and isinstance(
                    getattr(marker, "contents", None), dict
                ):
                    marker.contents.pop(name, None)
        except Exception:
            pass

        # 0.5) If a table with the same name already exists, allow this class
        # to extend it instead of raising duplicate-table errors.
        try:
            table_name = getattr(cls, "__tablename__", None)
            if table_name and table_name in Base.metadata.tables:
                table_args = getattr(cls, "__table_args__", None)
                if table_args is None:
                    cls.__table_args__ = {"extend_existing": True}
                elif isinstance(table_args, dict):
                    table_args = dict(table_args)
                    table_args["extend_existing"] = True
                    cls.__table_args__ = table_args
                elif isinstance(table_args, tuple):
                    if table_args and isinstance(table_args[-1], dict):
                        table_dict = dict(table_args[-1])
                        table_dict["extend_existing"] = True
                        cls.__table_args__ = (*table_args[:-1], table_dict)
                    else:
                        cls.__table_args__ = (*table_args, {"extend_existing": True})
        except Exception:
            pass

        # 1) Determine whether this class should be mapped.
        try:
            from sqlalchemy import Column as _SAColumn
            from sqlalchemy.orm import MappedColumn as _MappedColumn
        except Exception:  # pragma: no cover - defensive
            _SAColumn = None
            _MappedColumn = None

        def _has_mappable_columns() -> bool:
            for base in cls.__mro__:
                for attr in getattr(base, "__dict__", {}).values():
                    if _SAColumn is not None and isinstance(attr, _SAColumn):
                        return True
                    if _MappedColumn is not None and isinstance(attr, _MappedColumn):
                        return True
                    storage = getattr(attr, "storage", None)
                    if storage is not None:
                        return True
                mapping = getattr(base, "__tigrbl_cols__", None)
                if isinstance(mapping, dict):
                    for spec in mapping.values():
                        if _MappedColumn is not None and isinstance(
                            spec, _MappedColumn
                        ):
                            return True
                        storage = getattr(spec, "storage", None)
                        if storage is not None:
                            return True
            return False

        def _has_primary_key() -> bool:
            mapper_args = getattr(cls, "__mapper_args__", None)
            if isinstance(mapper_args, dict) and mapper_args.get("primary_key"):
                return True
            for base in cls.__mro__:
                for attr in getattr(base, "__dict__", {}).values():
                    if _SAColumn is not None and isinstance(attr, _SAColumn):
                        if getattr(attr, "primary_key", False):
                            return True
                    if _MappedColumn is not None and isinstance(attr, _MappedColumn):
                        if getattr(attr, "primary_key", False):
                            return True
                    storage = getattr(attr, "storage", None)
                    if storage is not None and getattr(storage, "primary_key", False):
                        return True
                mapping = getattr(base, "__tigrbl_cols__", None)
                if isinstance(mapping, dict):
                    for spec in mapping.values():
                        storage = getattr(spec, "storage", None)
                        if storage is not None and getattr(
                            storage, "primary_key", False
                        ):
                            return True
            return False

        explicit_abstract = "__abstract__" in cls.__dict__
        if not explicit_abstract:
            if not _has_mappable_columns() or not _has_primary_key():
                cls.__abstract__ = True
            else:
                cls.__abstract__ = False

        should_map = not getattr(cls, "__abstract__", False)

        # 1.5) BEFORE SQLAlchemy maps: turn ColumnSpecs into real mapped_column(...)
        _materialize_colspecs_to_sqla(cls, map_columns=should_map)
        _ensure_instrumented_attr_accessors()

        # 2) Let SQLAlchemy map the class (PK now exists)
        super().__init_subclass__(**kw)

        # 2.5) Surface ctx-only op declarations for lightweight introspection.
        if not hasattr(cls, "__tigrbl_ops__"):
            for attr in cls.__dict__.values():
                target = getattr(attr, "__func__", attr)
                if getattr(target, "__tigrbl_op_decl__", None) is not None:
                    cls.__tigrbl_ops__ = tuple()
                    break

        # 2.6) Collect response specs declared via @response_ctx
        try:
            from tigrbl.response import (
                get_attached_response_spec,
                get_attached_response_alias,
            )

            responses = {}
            for name, obj in cls.__dict__.items():
                spec = get_attached_response_spec(obj)
                if spec is None:
                    continue
                alias = get_attached_response_alias(obj) or name
                responses[alias] = spec
            if responses:
                cls.responses = responses
                cls.response = next(iter(responses.values()))
        except Exception:
            pass

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
