"""peagen.defaults.abuse
----------------------
Settings for abuse detection and rate limiting.
"""

BAN_THRESHOLD = 10
"""Number of unknown RPC calls before an IP is banned."""

__all__ = ["BAN_THRESHOLD"]
