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
def key_version_routes(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app_mod = importlib.reload(importlib.import_module("auto_kms.app"))
    return _route_map(app_mod.app, "KeyVersion")


@pytest.mark.parametrize(
    "alias,path,methods",
    [
        ("create", "/kms/key_version", {"POST"}),
        ("read", "/kms/key_version/{item_id}", {"GET"}),
        ("update", "/kms/key_version/{item_id}", {"PATCH"}),
        ("replace", "/kms/key_version/{item_id}", {"PUT"}),
        ("delete", "/kms/key_version/{item_id}", {"DELETE"}),
        ("list", "/kms/key_version", {"GET"}),
        ("clear", "/kms/key_version", {"DELETE"}),
        ("bulk_create", "/kms/key_version/bulk", {"POST"}),
        ("bulk_update", "/kms/key_version/bulk", {"PATCH"}),
        ("bulk_replace", "/kms/key_version/bulk", {"PUT"}),
        ("bulk_delete", "/kms/key_version/bulk", {"DELETE"}),
    ],
)
def test_key_version_default_op_verbs(key_version_routes, alias, path, methods):
    assert alias in key_version_routes
    got_path, got_methods = key_version_routes[alias]
    assert got_path.lower() == path.lower()
    assert got_methods == methods
