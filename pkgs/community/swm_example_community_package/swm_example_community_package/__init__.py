from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib


def _runtime_version() -> str:
    try:
        return version("swm_example_community_package")
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
            "version"
        ]


__version__ = _runtime_version()
__long_desc__ = """

# Swarmauri Example Plugin

This repository includes an example of a Swarmauri Plugin.

Visit us at: https://swarmauri.com
Follow us at: https://github.com/swarmauri
Star us at: https://github.com/swarmauri/swarmauri-sdk

"""
