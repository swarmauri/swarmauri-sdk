"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import pj


@pytest.mark.unit
def test_installed_version():
    assert pj.__version__ == version("pj") == "0.0.1.dev1"
