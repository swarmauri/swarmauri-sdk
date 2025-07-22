"""User model."""

from ._base import Base
from ..mixins import  (GUIDPk, 
Timestamped, TenantBound, Principal, AsyncCapable, ActiveToggle)
from ..types import Column, String, LargeBinary


class User(Base, GUIDPk, Timestamped, TenantBound, Principal, AsyncCapable, 
    ActiveToggle):
    __tablename__ = "users"
    username = Column(String(80), nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(LargeBinary(60))


__all__ = ["User"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
