"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_groq import GroqVLM as _GroqVLM

warnings.warn(
    "Importing GroqVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_groq.GroqVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

GroqVLM = _GroqVLM

__all__ = ["GroqVLM"]
