"""Expose the composition's receiving app through existing transports."""

from .login import OIDCAdmission


def document_app(workflow):
    """Return HttpApp; use .asgi with an existing ASGI server transport."""
    return workflow.runtime.endpoints["documents"]


__all__ = ["document_app", "OIDCAdmission"]
