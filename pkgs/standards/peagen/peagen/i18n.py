"""Simple internationalization helpers for Peagen."""

from __future__ import annotations

from typing import Dict


_MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "cli.app_help": "CLI tool for processing project files using Peagen.",
        "cli.init.local_help": "Bootstrap Peagen artefacts (project, template-set …) locally",
        "cli.init.remote_help": "Bootstrap Peagen artefacts (project, template-set …) via JSON-RPC",
    },
    "es": {
        "cli.app_help": "Herramienta CLI para procesar archivos de proyecto con Peagen.",
        "cli.init.local_help": "Crea artefactos de Peagen (proyecto, conjunto de plantillas…) localmente",
        "cli.init.remote_help": "Crea artefactos de Peagen (proyecto, conjunto de plantillas…) vía JSON-RPC",
    },
}

_language = "en"


def set_language(lang: str) -> None:
    """Set the active language namespace."""
    global _language
    if lang in _MESSAGES:
        _language = lang


def get_message(key: str) -> str:
    """Return the message for ``key`` in the active language."""
    return _MESSAGES.get(_language, {}).get(key, _MESSAGES["en"].get(key, key))
