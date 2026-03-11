"""Facade: ``tigrbl.mapping`` → ``tigrbl_canon.mapping``."""

import sys
from tigrbl_canon import mapping as _canon

# Replace this module with the canonical one so both import paths
# share the exact same module object and all mutable state.
sys.modules[__name__] = _canon
