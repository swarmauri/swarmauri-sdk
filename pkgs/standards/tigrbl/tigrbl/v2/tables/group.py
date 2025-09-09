"""Group model."""

from ._base import Base
from ..mixins import GUIDPk, Timestamped, TenantBound, Principal
from ..types import Column, String


class Group(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "groups"
    name = Column(String)


__all__ = ["Group"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
