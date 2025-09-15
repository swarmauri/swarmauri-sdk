from email.message import Message
from importlib.metadata import PackageNotFoundError

from swarmauri_tests_pylicense import DependencyPath, _collect_licenses

pytest_plugins = ["pytester"]


def test_parameterized_mode(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_dependency_paths",
        lambda pkg: [DependencyPath(("dummy", "dep"), "MIT", "1.0")],
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
    )
    result.assert_outcomes(passed=1)
    assert (
        "swarmauri_tests_pylicense:license::dummy::dep==1.0 [MIT]"
        in result.stdout.str()
    )


def test_aggregate_mode(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_dependency_paths",
        lambda pkg: [
            DependencyPath(("dummy", "dep"), "MIT", "1.0"),
            DependencyPath(("dummy", "dep2"), "Apache-2.0", "2.0"),
        ],
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
        "--pylicense-mode=aggregate",
    )
    result.assert_outcomes(passed=1)
    assert "license aggregate check for dummy" in result.stdout.str()


def test_classifier_fallback(monkeypatch):
    class DummyDist:
        def __init__(self) -> None:
            self.metadata = Message()
            self.metadata.add_header(
                "Classifier", "License :: OSI Approved :: MIT License"
            )
            self.requires = None
            self.version = "0"

    def fake_distribution(name):
        if name == "foo":
            return DummyDist()
        raise PackageNotFoundError

    monkeypatch.setattr("swarmauri_tests_pylicense.distribution", fake_distribution)
    licenses = _collect_licenses("foo")
    assert licenses["foo"].license == "MIT License"


def test_allow_disallow_lists(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_dependency_paths",
        lambda pkg: [DependencyPath(("dummy", "dep"), "GPL", "1.0")],
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
        "--pylicense-allow-list=MIT",
    )
    result.assert_outcomes(failed=1)
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
        "--pylicense-disallow-list=GPL",
    )
    result.assert_outcomes(failed=1)


def test_nonstandard_acceptance(pytester, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_tests_pylicense._collect_dependency_paths",
        lambda pkg: [DependencyPath(("dummy", "dep"), "Custom", "1.0")],
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
    )
    result.assert_outcomes(failed=1)
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=dummy",
        "--pylicense-accept-deps=dep",
    )
    result.assert_outcomes(passed=1)
