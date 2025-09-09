"""Org model."""

from ._base import Base
from ..mixins import GUIDPk, Timestamped, TenantBound, Principal
from ...specs import IO, F, acol, S
from ...types import Mapped, String


class Org(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "orgs"
    __abstract__ = True
    name: Mapped[str] = acol(
        storage=S(String),
        field=F(),
        io=IO(),
    )


__all__ = ["Org"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
