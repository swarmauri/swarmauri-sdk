from email.message import Message
from importlib.metadata import PackageNotFoundError


from swarmauri_tests_pylicense import _collect_licenses

pytest_plugins = ["pytester"]


def test_parameterized_mode(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_licenses", lambda pkg: {"dep": "MIT"}
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
    )
    result.assert_outcomes(passed=1)
    assert "swarmauri_tests_pylicense:license::dep" in result.stdout.str()


def test_aggregate_mode(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_licenses",
        lambda pkg: {"dep": "MIT", "dep2": "Apache-2.0"},
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
        "--pylicense-mode=aggregate",
    )
    result.assert_outcomes(passed=1)
    assert "license aggregate check" in result.stdout.str()


def test_classifier_fallback(monkeypatch):
    class DummyDist:
        def __init__(self) -> None:
            self.metadata = Message()
            self.metadata.add_header(
                "Classifier", "License :: OSI Approved :: MIT License"
            )
            self.requires = None

    def fake_distribution(name):
        if name == "foo":
            return DummyDist()
        raise PackageNotFoundError

    monkeypatch.setattr("swarmauri_tests_pylicense.distribution", fake_distribution)
    licenses = _collect_licenses("foo")
    assert licenses["foo"] == "MIT License"
