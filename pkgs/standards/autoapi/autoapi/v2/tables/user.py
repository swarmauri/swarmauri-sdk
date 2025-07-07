"""User model."""
from ._base import Base
from ..mixins import GUIDPk, Timestamped, TenantBound, Principal, AsyncCapable
from sqlalchemy import Column, String

class User(Base, GUIDPk, Timestamped, TenantBound, Principal, AsyncCapable):
    __tablename__ = "users"
    email = Column(String, unique=True)
    
__all__ = ["User"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]

def __dir__():
    # optional, keeps IPython completion tight
    return sorted(__all__)