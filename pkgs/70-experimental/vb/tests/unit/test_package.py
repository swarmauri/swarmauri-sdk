"""Verify that the installed placeholder exposes matching version metadata."""

from importlib.metadata import version

import pytest

import vb


@pytest.mark.unit
def test_installed_version():
    assert vb.__version__ == version("vb") == "0.0.1.dev1"
