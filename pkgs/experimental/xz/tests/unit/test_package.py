"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import xz


@pytest.mark.unit
def test_installed_version():
    assert xz.__version__ == version("xz") == "0.0.1.dev1"
