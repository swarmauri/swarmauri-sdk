"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_mistral import MistralVLM as _MistralVLM

warnings.warn(
    "Importing MistralVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_mistral.MistralVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

MistralVLM = _MistralVLM

__all__ = ["MistralVLM"]
