"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_gemini import GeminiVLM as _GeminiVLM

warnings.warn(
    "Importing GeminiVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_gemini.GeminiVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

GeminiVLM = _GeminiVLM

__all__ = ["GeminiVLM"]
