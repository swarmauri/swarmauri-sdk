from __future__ import annotations

from autoapi.v2.mixins import Bootstrappable
from autoapi.v2.tables import User as UserBase


class User(UserBase, Bootstrappable):
    pass


__all__ = ["User"]
