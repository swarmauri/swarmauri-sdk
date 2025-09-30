"""Signing facades and plugin stubs for the Swarmauri standards library."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _load_signer() -> type:
    try:
        return importlib.import_module("SignerNameTBD.Signer").Signer
    except ModuleNotFoundError:  # pragma: no cover - dev fallback
        plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "SignerNameTBD"
        if str(plugin_root) not in sys.path:
            sys.path.append(str(plugin_root))
        return importlib.import_module("SignerNameTBD.Signer").Signer


Signer = _load_signer()

__all__ = ["Signer"]
