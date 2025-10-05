from __future__ import annotations

from textwrap import dedent

pytest_plugins = ["pytester"]


def _write_pyproject(pytester, name: str = "demo_package") -> None:
    pytester.makefile(
        ".toml",
        pyproject=dedent(
            f"""
            [project]
            name = "{name}"
            version = "0.0.1"
            description = "demo"
            requires-python = ">=3.10"
            authors = [{{ name = "Tester" }}]
            readme = "README.md"
            license = {{ text = "Apache-2.0" }}
            """
        ),
    )


def _write_package(pytester, name: str = "demo_package") -> None:
    package_dir = pytester.path / name
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("value = 42\n")


def test_plugin_passes_without_warnings(pytester):
    _write_pyproject(pytester)
    _write_package(pytester)
    pytester.makeconftest(
        """
import swarmauri_tests_griffe


def pytest_configure(config):
    def silent_load(name, *, search_paths=None):
        return name

    swarmauri_tests_griffe.griffe.load = silent_load
"""
    )

    result = pytester.runpytest("-p", "swarmauri_tests_griffe", "-q")
    result.assert_outcomes(passed=1)


def test_plugin_fails_on_griffe_warning(pytester):
    _write_pyproject(pytester, name="warning_package")
    _write_package(pytester, name="warning_package")
    pytester.makeconftest(
        """
import warnings
import swarmauri_tests_griffe


def pytest_configure(config):
    def noisy_load(name, *, search_paths=None):
        warnings.warn("issued from griffe", UserWarning)
        return name

    swarmauri_tests_griffe.griffe.load = noisy_load
"""
    )

    result = pytester.runpytest("-p", "swarmauri_tests_griffe", "-q")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*Griffe emitted warnings while loading warning_package*",
        ]
    )
