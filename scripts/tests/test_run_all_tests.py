"""Regression coverage for compatibility-runner outcome classification."""

import importlib.util
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "run_all_tests", Path(__file__).parents[1] / "run_all_tests.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_missing_tests_are_not_a_failure(tmp_path):
    assert runner.test_directory(tmp_path) is None


def test_unit_tests_take_precedence_over_service_tests(tmp_path):
    unit = tmp_path / "tests/unit"
    unit.mkdir(parents=True)
    (unit / "test_example.py").write_text("def test_example(): pass")
    assert runner.test_directory(tmp_path) == unit


def test_empty_test_directory_is_missing_coverage(tmp_path):
    (tmp_path / "tests").mkdir()
    assert runner.test_directory(tmp_path) is None


def test_pytest_exit_codes_do_not_hide_collection_or_usage_errors():
    assert runner.test_status(0) == "passed"
    assert runner.test_status(5) == "no_tests_collected"
    for code in (1, 2, 3, 4, 124):
        assert runner.test_status(code) == "test_failed"


def test_dependency_closure_handles_cycles_and_name_normalization(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    packages = {
        "first": (first, {"project": {"dependencies": ["Second_Package>=1"]}}),
        "second-package": (second, {"project": {"dependencies": ["first"]}}),
    }
    assert runner.local_dependencies("first", packages) == [second, first]


def test_dependency_closure_does_not_force_an_incompatible_local_version(tmp_path):
    packages = {
        "legacy": (tmp_path / "legacy", {"project": {"dependencies": ["core<1"]}}),
        "core": (
            tmp_path / "core",
            {"project": {"version": "2.0", "dependencies": []}},
        ),
    }
    assert runner.local_dependencies("legacy", packages) == [tmp_path / "legacy"]


def test_native_payload_cannot_be_shared_as_a_universal_wheel(tmp_path):
    import zipfile
    import pytest

    wheel = tmp_path / "example-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("example/native.cp312-win_amd64.pyd", b"native")
    with pytest.raises(ValueError, match="Native library"):
        runner.universal_wheel(wheel)


def test_pure_python_wheel_can_be_shared(tmp_path):
    import zipfile

    wheel = tmp_path / "example-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("example/__init__.py", "")
    assert runner.universal_wheel(wheel)


def test_report_retries_a_transient_windows_reader_lock(tmp_path, monkeypatch):
    original = Path.replace
    attempts = []

    def replace(path, target):
        attempts.append(path)
        if len(attempts) == 1:
            raise PermissionError("reader still has report open")
        return original(path, target)

    monkeypatch.setattr(Path, "replace", replace)
    monkeypatch.setattr(runner.time, "sleep", lambda _: None)
    report = tmp_path / "results.json"
    runner.write_report(report, [{"status": "no_tests"}])
    assert len(attempts) == 2
    assert '"no_tests"' in report.read_text()
