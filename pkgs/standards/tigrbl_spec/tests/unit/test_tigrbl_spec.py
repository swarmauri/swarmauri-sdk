import tigrbl_spec


def test_exports_version() -> None:
    assert isinstance(tigrbl_spec.__version__, str)
    assert tigrbl_spec.__version__
