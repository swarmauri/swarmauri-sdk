"""
Shared declarative base & metadata
----------------------------------
Other model modules import `Base` from here.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        try:
            from autoapi.v3.bindings.model import bind
            bind(cls)   # safe/idempotent; v3 binders handle rebinds later
        except Exception:
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

    # Optional: default __tablename__ if you like
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()  # "tenant" / "user" / "group"


__all__ = ["Base"]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
