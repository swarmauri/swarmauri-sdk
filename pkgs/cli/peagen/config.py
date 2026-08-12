from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG_NAME = ".peagen.toml"


def load_config(
    config_path: Optional[str | Path] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    path = Path(config_path) if config_path else Path.cwd() / DEFAULT_CONFIG_NAME
    config: Dict[str, Any] = {}

    if path.is_file():
        with path.open("rb") as fh:
            loaded = tomllib.load(fh)
            if isinstance(loaded, dict):
                config = loaded

    if output_dir is not None:
        config["output_dir"] = output_dir

    return config


def resolve_config(
    config_path: Optional[str | Path] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    return load_config(config_path=config_path, output_dir=output_dir)
