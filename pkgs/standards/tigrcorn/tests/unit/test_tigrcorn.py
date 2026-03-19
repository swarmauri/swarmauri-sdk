import tigrcorn


def test_exports_version() -> None:
    assert isinstance(tigrcorn.__version__, str)
    assert tigrcorn.__version__
