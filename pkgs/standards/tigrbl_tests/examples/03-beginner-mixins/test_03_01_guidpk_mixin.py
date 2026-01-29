from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk


def test_guidpk_mixin_primary_key() -> None:
    class Gadget(Base, GUIDPk):
        __tablename__ = "guidpk_gadgets"

    assert Gadget.id.storage.primary_key is True
    assert getattr(Gadget.id.storage.type_, "as_uuid", False) is True
