"""
AutoAPI hooks for Peagen Gateway.
Import all hook modules to register them with the AutoAPI instance.
"""

# Import all hook modules to register them
from . import keys, pools, secrets, tasks, workers

# Import the global error handler
from .common import global_error_handler

# Export all modules for convenience
__all__ = ["tasks", "workers", "pools", "secrets", "keys", "global_error_handler"]
