"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_openai import OpenAIVLM as _OpenAIVLM

warnings.warn(
    "Importing OpenAIVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_openai.OpenAIVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

OpenAIVLM = _OpenAIVLM

__all__ = ["OpenAIVLM"]
