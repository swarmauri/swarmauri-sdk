from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def _router_paths(api, name: str) -> set[str]:
    router = api.routers.get(name)
    return {r.path for r in getattr(router, "routes", [])}


def test_default_resource_and_rpc_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    api = TigrblApp()
    api.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(api, "Item")}
    assert "/item" in paths
    assert hasattr(api.rpc, "Item")


def test_resource_override_affects_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        __resource__ = "test"
        name = Column(String, nullable=False)

    api = TigrblApp()
    api.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(api, "Item")}
    assert "/test" in paths
    assert hasattr(api.rpc, "Test")
