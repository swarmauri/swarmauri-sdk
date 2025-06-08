import pytest
from pathlib import Path

from peagen.handlers import mutate


@pytest.mark.unit
def test_mutate_module_is_empty():
    source = Path(mutate.__file__).read_text()
    assert source.strip() == ""
