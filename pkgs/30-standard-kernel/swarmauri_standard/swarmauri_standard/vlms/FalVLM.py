"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_falai import FalVLM as _FalVLM

warnings.warn(
    "Importing FalVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_falai.FalVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

FalVLM = _FalVLM

__all__ = ["FalVLM"]
