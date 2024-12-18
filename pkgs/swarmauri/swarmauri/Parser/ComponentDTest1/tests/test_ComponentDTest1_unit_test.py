import pytest
from ComponentDTest1 import __version__

def test_version():
    assert __version__ == "0.1.0"
