import time
from dataclasses import replace
import pytest
from swarmauri_core.permissions import Permission
from swarmauri_core.delegation import Grant, GrantConflictError
from swarmauri_grantstore_sqlite import SqliteGrantStore

pytestmark = pytest.mark.unit


def test_restart_preserves_ancestry_and_revocation(tmp_path):
    path = tmp_path / "grants.db"
    store = SqliteGrantStore(path=path)
    root = Grant(
        "root",
        "task",
        "alice",
        "A",
        "tenant",
        (Permission("read", "doc", "tenant"),),
        int(time.time()) + 60,
        2,
    )
    child = replace(
        root, grant_id="child", parent_id="root", holder="B", remaining_depth=1
    )
    store.create(root)
    store.create(child)
    reopened = SqliteGrantStore(path=path)
    assert reopened.load("child").parent_id == "root"
    assert reopened.save(replace(root, revoked=True)).revision == 1
    with pytest.raises(GrantConflictError):
        store.save(root)
    assert store.load("root").revoked
