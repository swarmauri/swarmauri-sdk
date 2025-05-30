import random; random.seed(0xA11A)
import pytest
from peagen import _config


@pytest.mark.unit
def test_version_present():
    assert isinstance(_config.__version__, str)
    assert _config.__version__
