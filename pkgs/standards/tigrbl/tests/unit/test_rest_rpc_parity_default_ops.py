import pytest


from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk, BulkCapable, Mergeable
from tigrbl.orm.tables import Base
from tigrbl.op.types import CANON
from tigrbl.types import Column, String


def _route_map(router) -> dict[str, tuple[str, set[str]]]:
    out: dict[str, tuple[str, set[str]]] = {}
    for r in getattr(router, "routes", []):
        if hasattr(r, "name"):
            name = getattr(r, "name")
            path = getattr(r, "path")
            methods = set(getattr(r, "methods", []) or [])
        else:  # pragma: no cover - fallback when FastAPI is missing
            path, methods, _, opts = r
            name = opts.get("name")
            methods = set(methods)
        if name and "." in name:
            alias = name.split(".", 1)[1]
            out[alias] = (path, methods)
    return out


@pytest.mark.parametrize(
    "alias,target,path,methods",
    [
        ("create", "create", "/item", {"POST"}),
        ("read", "read", "/item/{item_id}", {"GET"}),
        ("update", "update", "/item/{item_id}", {"PATCH"}),
        ("replace", "replace", "/item/{item_id}", {"PUT"}),
        ("delete", "delete", "/item/{item_id}", {"DELETE"}),
        ("list", "list", "/item", {"GET"}),
        ("clear", "clear", "/item", {"DELETE"}),
        ("merge", "merge", "/item/{item_id}", {"PATCH"}),
        ("bulk_create", "bulk_create", "/item", {"POST"}),
        ("bulk_update", "bulk_update", "/item", {"PATCH"}),
        ("bulk_replace", "bulk_replace", "/item", {"PUT"}),
        ("bulk_merge", "bulk_merge", "/item", {"PATCH"}),
        ("bulk_delete", "bulk_delete", "/item", {"DELETE"}),
    ],
)
def test_rest_rpc_parity_for_default_verbs(alias, target, path, methods):
    Base.metadata.clear()

    class Item(Base, GUIDPk, BulkCapable, Mergeable):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    Item.__tigrbl_ops__ = {verb: {"target": verb} for verb in CANON if verb != "custom"}

    api = TigrblApp()
    api.include_model(Item, mount_router=False)

    routes = _route_map(Item.rest.router)
    if alias == "clear" and "bulk_delete" in routes:
        assert alias not in routes
    elif alias == "create" and "bulk_create" in routes:
        assert alias not in routes
    else:
        assert alias in routes
        got_path, got_methods = routes[alias]
        assert got_path.lower() == path.lower()
        assert got_methods == methods

    assert hasattr(api.rpc.Item, alias)


def test_non_bulkcapable_prefers_create() -> None:
    Base.metadata.clear()

    class Item(Base, GUIDPk, Mergeable):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    api = TigrblApp()
    api.include_model(Item, mount_router=False)

    routes = _route_map(Item.rest.router)
    assert "bulk_create" not in routes
    assert "create" in routes
    assert hasattr(api.rpc.Item, "create")
    assert not hasattr(api.rpc.Item, "bulk_create")
