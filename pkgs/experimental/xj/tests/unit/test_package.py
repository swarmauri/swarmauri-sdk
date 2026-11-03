"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import xj


@pytest.mark.unit
def test_installed_version():
    assert xj.__version__ == version("xj") == "0.0.1.dev1"
