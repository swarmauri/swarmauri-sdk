import pytest


@pytest.mark.unit
def test_import():
    import cayaml
    assert dir(cayaml)
