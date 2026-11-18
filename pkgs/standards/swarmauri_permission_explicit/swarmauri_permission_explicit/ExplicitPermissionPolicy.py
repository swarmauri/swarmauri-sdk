"""Exact-match resource authorization and permission attenuation."""

from typing import Literal
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.permissions import PermissionPolicyBase
from swarmauri_core.permissions import AuthorizationDecision


@ComponentBase.register_type(PermissionPolicyBase, "ExplicitPermissionPolicy")
class ExplicitPermissionPolicy(PermissionPolicyBase):
    """Deny unless the exact action, resource and tenant were admitted."""

    type: Literal["ExplicitPermissionPolicy"] = "ExplicitPermissionPolicy"

    def authorize(self, available, requested):
        allowed = requested in available
        return AuthorizationDecision(allowed, "" if allowed else "Not granted")

    def attenuate(self, available, requested):
        if not requested or not set(requested).issubset(available):
            raise PermissionError("Cannot expand authority")
        return tuple(dict.fromkeys(requested))
