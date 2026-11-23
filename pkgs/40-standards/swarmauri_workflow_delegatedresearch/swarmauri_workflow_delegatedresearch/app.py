"""Expose role-specific receiving apps through existing transports."""


def role_app(workflow, role):
    """Return HttpApp; .asgi adapts it to an existing ASGI host."""
    return workflow.runtime.endpoints[role]
