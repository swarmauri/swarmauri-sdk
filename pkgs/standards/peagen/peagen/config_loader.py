"""Utility class for loading peagen TOML configurations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import dotenv_values
from jinja2 import Environment

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore


class TomlConfigLoader:
    """Load ``.peagen.toml`` files and expose their data."""

    def __init__(
        self,
        path: Optional[Path] = None,
        start_dir: Optional[Path] = None,
        env_file: Optional[Path] = None,
    ) -> None:
        self.path = path or self._discover(start_dir or Path.cwd())
        self.env_file = env_file
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
        text = path.read_text(encoding="utf-8")

        env = Environment(autoescape=False)

        env_path = self.env_file or path.with_suffix(".env")
        values = dotenv_values(env_path) if env_path.is_file() else {}
        secrets = self._to_nested(values)

        rendered = env.from_string(text).render(secrets=secrets)
        return tomllib.loads(rendered)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def _to_nested(self, values: Dict[str, str]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for k, v in values.items():
            parts = k.split(".")
            cur = data
            for part in parts[:-1]:
                cur = cur.setdefault(part, {})
            cur[parts[-1]] = v
        return data



