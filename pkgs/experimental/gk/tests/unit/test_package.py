"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import gk


@pytest.mark.unit
def test_installed_version():
    assert gk.__version__ == version("gk") == "0.0.1.dev1"
