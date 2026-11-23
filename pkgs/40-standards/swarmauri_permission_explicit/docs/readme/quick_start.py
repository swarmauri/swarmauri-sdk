from swarmauri_core.permissions import Permission
from swarmauri_permission_explicit import ExplicitPermissionPolicy

policy = ExplicitPermissionPolicy()
read = Permission("documents:read", "document:123", "acme")
assert policy.authorize((read,), read).allowed
assert policy.attenuate((read,), (read,)) == (read,)
# Different actions, documents or tenants are denied.
