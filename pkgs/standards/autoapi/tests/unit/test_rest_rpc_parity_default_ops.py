import pytest

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.mixins import GUIDPk, BulkCapable
from autoapi.v3.opspec.types import CANON
from autoapi.v3.tables import Base
from autoapi.v3.types import Column, String


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
        ("upsert", "upsert", "/item", {"PATCH"}),
        ("bulk_create", "bulk_create", "/item", {"POST"}),
        ("bulk_update", "bulk_update", "/item", {"PATCH"}),
        ("bulk_replace", "bulk_replace", "/item", {"PUT"}),
        ("bulk_upsert", "bulk_upsert", "/item", {"PATCH"}),
        ("bulk_delete", "bulk_delete", "/item", {"DELETE"}),
    ],
)
def test_rest_rpc_parity_for_default_verbs(alias, target, path, methods):
    Base.metadata.clear()

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        name = Column(String, nullable=False)

    Item.__autoapi_ops__ = {
        verb: {"target": verb} for verb in CANON if verb != "custom"
    }

    api = AutoAPI()
    api.include_model(Item, mount_router=False)

    routes = _route_map(Item.rest.router)
    assert alias in routes
    got_path, got_methods = routes[alias]
    assert got_path.lower() == path.lower()
    assert got_methods == methods

    assert hasattr(api.rpc.Item, alias)
