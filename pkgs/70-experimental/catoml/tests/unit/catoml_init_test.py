import pytest


@pytest.mark.unit
def test_import():
    import catoml

    assert dir(catoml)
