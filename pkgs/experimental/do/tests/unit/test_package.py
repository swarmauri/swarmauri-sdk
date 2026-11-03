"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import do


@pytest.mark.unit
def test_installed_version():
    assert do.__version__ == version("do") == "0.0.1.dev1"
