from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


<<<<<<< HEAD
def _router_paths(app, name: str) -> set[str]:
    router = app.routers.get(name)
=======
def _router_paths(router, name: str) -> set[str]:
    router = router.routers.get(name)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    return {r.path for r in getattr(router, "routes", [])}


def test_default_resource_and_rpc_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

<<<<<<< HEAD
    app = TigrblApp()
    app.include_table(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(app, "Item")}
    assert "/item" in paths
    assert hasattr(app.rpc, "Item")
=======
    router = TigrblApp()
    router.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(router, "Item")}
    assert "/item" in paths
    assert hasattr(router.rpc, "Item")
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c


def test_resource_override_affects_prefixes():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        __resource__ = "test"
        name = Column(String, nullable=False)

<<<<<<< HEAD
    app = TigrblApp()
    app.include_table(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(app, "Item")}
    assert "/test" in paths
    assert hasattr(app.rpc, "Test")
=======
    router = TigrblApp()
    router.include_model(Item, mount_router=False)

    paths = {p.lower() for p in _router_paths(router, "Item")}
    assert "/test" in paths
    assert hasattr(router.rpc, "Test")
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
