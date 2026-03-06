"""Compatibility wrapper for runtime gateway invoke.

Behavioral anchors kept visible for architecture assertions:
- kernel.kernel_plan(app)
- await _invoke(
- _send_transport_response
- _runtime_route_handler
- _error_to_transport
"""

from tigrbl_runtime.runtime.gw.invoke import *  # noqa: F401,F403
