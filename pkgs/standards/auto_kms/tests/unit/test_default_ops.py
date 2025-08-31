import auto_kms.app  # noqa: F401 ensures models are bound
from auto_kms.orm import Key
from auto_kms.orm import KeyVersion
import pytest

DEFAULT_OPS = {
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
}

RESOURCES = [("key", Key), ("key_version", KeyVersion)]


@pytest.mark.parametrize("resource, model", RESOURCES)
@pytest.mark.parametrize("verb", sorted(DEFAULT_OPS))
def test_default_op_registered(resource, model, verb):
    specs = model.opspecs.by_alias.get(verb) or []
    assert specs, f"{verb} not registered for {resource}"
    assert any(sp.target == verb for sp in specs)
