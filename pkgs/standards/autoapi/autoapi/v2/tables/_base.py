"""
Shared declarative base & metadata
----------------------------------
Other model modules import `Base` from here.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData
from types import SimpleNamespace
from ..impl.model_facets import init_model_facets  # NEW


class Base(DeclarativeBase):
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

        if getattr(cls, "__abstract__", False):
            return
        # Stable namespaces present immediately on class creation
        if not hasattr(cls, "opspecs"):
            cls.opspecs = SimpleNamespace()
        if not hasattr(cls, "schemas"):
            cls.schemas = SimpleNamespace()
        if not hasattr(cls, "methods"):
            cls.methods = SimpleNamespace()
        if not hasattr(cls, "rpc"):
            cls.rpc = SimpleNamespace()
        if not hasattr(cls, "core"):
            cls.core = SimpleNamespace()
        if not hasattr(cls, "core_raw"):
            cls.core_raw = SimpleNamespace()
        if not hasattr(cls, "handlers"):
            cls.handlers = SimpleNamespace()
        if not hasattr(cls, "handlers_raw"):
            cls.handlers_raw = SimpleNamespace()
        if not hasattr(cls, "hooks"):
            cls.hooks = SimpleNamespace()
        # Optional per-API registry (if you want to track multiple bindings)
        if not hasattr(cls, "__autoapi__"):
            meta = SimpleNamespace()
            meta.bindings = {}  # id(api) → dict(namespaces)
            setattr(cls, "__autoapi__", meta)

        # The table must be mapped at this point
        if hasattr(cls, "__table__") and cls.__table__ is not None:
            init_model_facets(cls)

    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(column_0_name)s_%(constraint_type)s",
        }
    )

    # Optional: default __tablename__ if you like
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()  # "tenant" / "user" / "group"


__all__ = ["Base"]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
