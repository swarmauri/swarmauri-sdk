# peagen/_utils/config_loader.py

import toml
from pathlib import Path
from typing import Any, Dict

def load_peagen_toml(path: Path | str = ".peagen.toml") -> Dict[str, Any]:
    """
    Read .peagen.toml from disk (or from `path`) and return its contents as a dict.
    Raise FileNotFoundError if not found.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Could not find {path!r}")
    return toml.loads(p.read_text())
