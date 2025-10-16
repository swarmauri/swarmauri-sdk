"""Top level exports for the :mod:`swarmauri_core` package."""

from swarmauri_core.billing.interfaces import (
    ALL_API_STRATEGIES,
    ALL_CAPABILITIES,
    Capability,
    IBillingProvider,
    Operation,
)

__version__ = "0.5.1.dev8"
__long_desc__ = """
# Swarmauri Core

## Core
- **Core Interfaces**: Define the fundamental communication and data-sharing protocols between components in a Swarmauri-based system.


Visit us at: https://swarmauri.com
Follow us at: https://github.com/swarmauri



"""

__all__ = [
    "ALL_API_STRATEGIES",
    "ALL_CAPABILITIES",
    "Capability",
    "IBillingProvider",
    "Operation",
]
