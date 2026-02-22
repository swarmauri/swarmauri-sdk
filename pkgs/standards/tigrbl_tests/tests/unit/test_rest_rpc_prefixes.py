from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def _router_paths(router, name: str) -> set[str]:
    router = router.routers.get(name)
    return {r.path for r in getattr(router, "routes", [])}


def test_default_resource_and_rpc_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    router = TigrblApp()
    router.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(router, "Item")}
    assert "/item" in paths
    assert hasattr(router.rpc, "Item")


def test_resource_override_affects_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        __resource__ = "test"
        name = Column(String, nullable=False)

    router = TigrblApp()
    router.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(router, "Item")}
    assert "/test" in paths
    assert hasattr(router.rpc, "Test")
