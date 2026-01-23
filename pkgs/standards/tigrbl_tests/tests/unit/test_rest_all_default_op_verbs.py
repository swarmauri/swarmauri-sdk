import pytest
from tigrbl.bindings.rest import build_router_and_attach
from tigrbl.orm.mixins import GUIDPk
from tigrbl.op import OpSpec
from tigrbl.orm.tables import Base
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
        ("custom_op", "custom", "/item/custom_op", {"POST"}),
    ],
)
def test_rest_default_op_verbs(alias, target, path, methods):
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    build_router_and_attach(Item, [OpSpec(alias=alias, target=target)])

    routes = _route_map(Item.rest.router)
    assert alias in routes
    got_path, got_methods = routes[alias]
    assert got_path.lower() == path.lower()
    assert got_methods == methods
