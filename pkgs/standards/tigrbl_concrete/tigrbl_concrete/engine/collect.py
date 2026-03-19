"""Compatibility wrapper for engine collection APIs.

``tigrbl_canon`` is deprecated. Keep the public ``collect_engine_config``
entrypoint by delegating to the first-class engine binder helpers.
"""

from __future__ import annotations

from tigrbl_concrete.engine.bind import collect_engine_bindings as collect_engine_config

__all__ = ["collect_engine_config"]
