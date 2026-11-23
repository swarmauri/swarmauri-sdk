"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_hyperbolic import HyperbolicVLM as _HyperbolicVLM

warnings.warn(
    "Importing HyperbolicVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_hyperbolic.HyperbolicVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

HyperbolicVLM = _HyperbolicVLM

__all__ = ["HyperbolicVLM"]
