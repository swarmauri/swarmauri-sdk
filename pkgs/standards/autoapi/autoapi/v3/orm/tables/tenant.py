"""Tenant model."""

from ._base import Base
from ..mixins import GUIDPk, Slugged, Timestamped


class Tenant(Base, GUIDPk, Slugged, Timestamped):
    __tablename__ = "tenants"
    __abstract__ = True


__all__ = ["Tenant"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""
    return sorted(__all__)
