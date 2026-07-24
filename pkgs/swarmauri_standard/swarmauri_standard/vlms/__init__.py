"""Lazy compatibility shims for deprecated VLM import paths.

Provider implementations live in their dedicated community packages.  The
provider module is imported only when the corresponding shim is requested.
"""

from importlib import import_module

__all__ = [
    "FalVLM",
    "GroqVLM",
    "HyperbolicVLM",
    "OpenAIVLM",
    "GeminiVLM",
    "AnthropicVLM",
    "MistralVLM",
]


def __getattr__(name: str):
    """Load only the requested provider compatibility shim."""
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{name}")
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
