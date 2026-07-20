"""Compatibility shims for deprecated swarmauri_standard.vlms locations.

VLM implementations now live in their dedicated provider packages.
"""

import warnings

from swarmauri_llm_anthropic import AnthropicVLM as _AnthropicVLM

warnings.warn(
    "Importing AnthropicVLM from swarmauri_standard.vlms is deprecated. "
    "Use swarmauri_llm_anthropic.AnthropicVLM instead.",
    DeprecationWarning,
    stacklevel=2,
)

AnthropicVLM = _AnthropicVLM

__all__ = ["AnthropicVLM"]
