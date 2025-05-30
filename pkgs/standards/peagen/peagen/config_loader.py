"""Utility class for loading peagen TOML configurations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore


class TomlConfigLoader:
    """Load ``.peagen.toml`` files and expose their data."""

    def __init__(self, path: Optional[Path] = None, start_dir: Optional[Path] = None) -> None:
        self.path = path or self._discover(start_dir or Path.cwd())
        self.config: Dict[str, Any] = {}
        if self.path:
            self.config = self._load(self.path)

    def _discover(self, start: Path) -> Optional[Path]:
        for folder in [start, *start.parents]:
            candidate = folder / ".peagen.toml"
            if candidate.is_file():
                return candidate
        return None

    def _load(self, path: Path) -> Dict[str, Any]:
        with path.open("rb") as f:
            return tomllib.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)


