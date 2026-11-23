"""Shared permissions contracts and immutable records."""

from .models import Permission, AuthorizationDecision
from .IPermissionPolicy import IPermissionPolicy

__all__ = ["IPermissionPolicy", "Permission", "AuthorizationDecision"]
