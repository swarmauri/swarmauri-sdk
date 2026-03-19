"""Diagnostic endpoint exposing kernel phase plans."""

from __future__ import annotations

from typing import Any

from ...runtime.kernel import _default_kernel as K


def build_kernelz_endpoint(router: Any):
    """Return an async handler that serves the Kernel's cached plan."""

    async def _kernelz():
        K.ensure_primed(router)
        payload = K.kernelz_payload(router)
        models = getattr(router, "models", {}) or {}
        if not models:
            return payload

        out = payload
        for model_name, model in models.items():
            specs = getattr(getattr(model, "opspecs", None), "all", ()) or ()
            if specs:
                continue
            model_map = payload.get(model_name)
            if not isinstance(model_map, dict):
                continue
            if out is payload:
                out = {
                    name: {alias: list(seq) for alias, seq in ops.items()}
                    for name, ops in payload.items()
                }
            enriched = out.get(model_name)
            if not isinstance(enriched, dict):
                continue
            for alias, seq in list(enriched.items()):
                extras = []
                seen = set(seq)
                for label in seq:
                    if not isinstance(label, str) or ":" not in label:
                        continue
                    raw = label.split(":", 1)[1]
                    if raw not in seen:
                        extras.append(raw)
                        seen.add(raw)
                if extras:
                    enriched[alias] = [*seq, *extras]
        return out

    return _kernelz


__all__ = ["build_kernelz_endpoint"]
