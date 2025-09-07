"""Diagnostic endpoint exposing kernel phase plans."""

from __future__ import annotations

from typing import Any

from ...runtime.kernel import _default_kernel as K


def build_kernelz_endpoint(api: Any):
    K.ensure_primed(api)

    async def _kernelz():
        return K.kernelz_payload(api)

    return _kernelz


__all__ = ["build_kernelz_endpoint"]
