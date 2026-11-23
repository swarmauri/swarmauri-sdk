"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import xk


@pytest.mark.unit
def test_installed_version():
    assert xk.__version__ == version("xk") == "0.0.1.dev1"
