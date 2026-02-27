"""Expose the repository ``examples`` tree under ``tigrbl_tests.examples``."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[2] / "examples")]
