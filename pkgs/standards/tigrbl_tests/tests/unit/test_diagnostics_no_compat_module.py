import importlib.util


def test_diagnostics_compat_module_removed() -> None:
    assert importlib.util.find_spec("tigrbl.system.diagnostics.compat") is None
