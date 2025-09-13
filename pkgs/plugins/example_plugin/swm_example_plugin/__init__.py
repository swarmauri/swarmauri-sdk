try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib

try:
    __version__ = version("swm-example-plugin")
except PackageNotFoundError:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        __version__ = tomllib.load(f)["project"]["version"]

__long_desc__ = """
# Swarmauri Example Plugin

This repository includes an example of a Swarmauri Plugin.

Visit us at: https://swarmauri.com
Follow us at: https://github.com/swarmauri
Star us at: https://github.com/swarmauri/swarmauri-sdk

"""
