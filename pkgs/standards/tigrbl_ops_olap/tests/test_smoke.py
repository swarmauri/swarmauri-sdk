import importlib.util


def test_package_namespace_available() -> None:
    assert importlib.util.find_spec("tigrbl_ops_olap") is not None
