"""Diagnostic endpoint exposing kernel phase plans."""

from __future__ import annotations

from typing import Any

from ...runtime.kernel import _default_kernel as K


def build_kernelz_endpoint(router: Any):
    """Return an async handler that serves the Kernel's cached plan."""

    async def _kernelz():
        K.ensure_primed(router)
        return K.kernelz_payload(router)

    return _kernelz


__all__ = ["build_kernelz_endpoint"]
