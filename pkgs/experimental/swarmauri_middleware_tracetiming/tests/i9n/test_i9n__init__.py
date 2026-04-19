from importlib import import_module


def test_import_package() -> None:
    module = import_module("swarmauri_middleware_tracetiming")
    assert module.__name__ == "swarmauri_middleware_tracetiming"
