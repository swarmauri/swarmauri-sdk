"""Expose the repository ``tests`` tree under ``tigrbl_tests.tests``."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[2] / "tests")]
