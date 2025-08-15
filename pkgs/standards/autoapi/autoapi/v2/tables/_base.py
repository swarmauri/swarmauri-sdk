"""
Shared declarative base & metadata
----------------------------------
Other model modules import `Base` from here.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData
from types import SimpleNamespace
# from ..impl.model_facets import init_model_facets  # NEW


class Base(DeclarativeBase):


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
