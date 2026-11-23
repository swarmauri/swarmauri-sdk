import mto


def test_mto_placeholder_metadata():
    assert mto.__version__ == "0.1.0"
    assert mto.PLANNING_STAGE is True
    assert mto.INTENDED_SCOPE == "monotone operators"
