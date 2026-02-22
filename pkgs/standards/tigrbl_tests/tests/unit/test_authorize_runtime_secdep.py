from __future__ import annotations

from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk


def test_authorize_is_injected_as_runtime_secdep() -> None:
    def authorize(request, model, alias, payload, user):
        return None

    class Item(Base, GUIDPk):
        __tablename__ = "authorize_runtime_secdep_item"
        name = Column(String, nullable=False)
        __tigrbl_ops__ = (OpSpec(alias="create", target="create"),)

    router = TigrblApp()
    router.set_auth(authorize=authorize)
    router.include_model(Item)

    spec = Item.ops.by_alias["create"][0]
    secdeps = tuple(spec.secdeps)
    dep_names = tuple(getattr(dep, "__tigrbl_dep_name__", "") for dep in secdeps)

    assert "security.authorize" in dep_names
