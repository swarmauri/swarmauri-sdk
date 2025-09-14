import importlib
import pytest


def _route_map(app, resource: str) -> dict[str, tuple[str, set[str]]]:
    out: dict[str, tuple[str, set[str]]] = {}
    for r in getattr(app, "routes", []):
        name = getattr(r, "name", "")
        if name.startswith(f"{resource}."):
            alias = name.split(".", 1)[1]
            out[alias] = (r.path, set(getattr(r, "methods", []) or []))
    return out


@pytest.fixture
def key_routes(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app_mod = importlib.reload(importlib.import_module("tigrbl_kms.app"))
    return _route_map(app_mod.app, "Key")


@pytest.mark.parametrize(
    "alias,path,methods",
    [
        ("read", "/kms/key/{item_id}", {"GET"}),
        ("update", "/kms/key/{item_id}", {"PATCH"}),
        ("replace", "/kms/key/{item_id}", {"PUT"}),
        ("delete", "/kms/key/{item_id}", {"DELETE"}),
        ("list", "/kms/key", {"GET"}),
        ("bulk_create", "/kms/key", {"POST"}),
        ("bulk_update", "/kms/key", {"PATCH"}),
        ("bulk_replace", "/kms/key", {"PUT"}),
        ("bulk_delete", "/kms/key", {"DELETE"}),
    ],
)
def test_key_default_op_verbs(key_routes, alias, path, methods):
    assert alias in key_routes
    got_path, got_methods = key_routes[alias]
    assert got_path.lower() == path.lower()
    assert got_methods == methods


def test_key_create_overridden(key_routes):
    assert "create" not in key_routes


def test_key_create_schemas_present():
    from tigrbl_kms.orm import Key

    assert hasattr(Key.schemas, "create")
    assert hasattr(Key.schemas, "bulk_create")
