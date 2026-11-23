"""Verify installed distribution metadata without importing stdlib uu."""

from importlib.metadata import version

import pytest


@pytest.mark.unit
def test_installed_version():
    assert version("uu") == "0.0.1.dev1"
