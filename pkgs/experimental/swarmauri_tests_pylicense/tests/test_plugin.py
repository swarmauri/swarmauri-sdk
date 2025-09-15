from swarmauri_tests_pylicense import _collect_licenses

pytest_plugins = ["pytester"]


def test_parameterized_mode(pytester):
    count = len(_collect_licenses("pytest"))
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=pytest",
    )
    result.assert_outcomes(passed=count)
    assert "swarmauri_tests_pylicense:license::pytest" in result.stdout.str()


def test_aggregate_mode(pytester):
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_pylicense",
        "--pylicense-package=pytest",
        "--pylicense-mode=aggregate",
    )
    result.assert_outcomes(passed=1)
    assert "license aggregate check" in result.stdout.str()


def test_classifier_detection():
    licenses = _collect_licenses("packaging")
    assert licenses["packaging"] != "UNKNOWN"


def test_license_file_detection():
    licenses = _collect_licenses("click")
    assert licenses["click"] != "UNKNOWN"
