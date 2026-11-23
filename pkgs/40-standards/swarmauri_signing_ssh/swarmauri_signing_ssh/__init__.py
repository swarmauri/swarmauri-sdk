"""
SSH-based signing utilities for the Swarmauri framework.

This package exposes the :class:`SshEnvelopeSigner` which provides
OpenSSH-compatible detached signatures over raw payloads and structured
envelopes.
"""

from .SshEnvelopeSigner import SshEnvelopeSigner

__all__ = ["SshEnvelopeSigner"]
