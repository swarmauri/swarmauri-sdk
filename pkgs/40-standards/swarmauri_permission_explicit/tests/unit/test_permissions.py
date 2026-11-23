import pytest
from swarmauri_core.permissions import Permission
from swarmauri_permission_explicit import ExplicitPermissionPolicy

pytestmark = pytest.mark.unit


def test_exact_resource_action_and_tenant():
    policy = ExplicitPermissionPolicy()
    admitted = Permission("read", "document:123", "a")
    assert policy.authorize((admitted,), admitted).allowed
    for requested in (
        Permission("write", "document:123", "a"),
        Permission("read", "document:456", "a"),
        Permission("read", "document:123", "b"),
        Permission("read", "*", "a"),
    ):
        assert not policy.authorize((admitted,), requested).allowed
        with pytest.raises(PermissionError):
            policy.attenuate((admitted,), (requested,))
    with pytest.raises(PermissionError):
        policy.attenuate((admitted,), ())
