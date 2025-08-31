"""User model."""

from ._base import Base
from ..mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    Principal,
    AsyncCapable,
    ActiveToggle,
)
from ...specs import IO, acol, F, S
from ...types import Mapped, String


class User(
    Base, GUIDPk, Timestamped, TenantBound, Principal, AsyncCapable, ActiveToggle
):
    __tablename__ = "users"
    __abstract__ = True
    username: Mapped[str] = acol(
        storage=S(String(32), nullable=False),
        field=F(constraints={"max_length": 32}),
        io=IO(),
    )


__all__ = ["User"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
