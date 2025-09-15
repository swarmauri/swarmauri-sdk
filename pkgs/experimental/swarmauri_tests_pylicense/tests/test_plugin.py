from swarmauri_tests_pylicense import _collect_licenses

pytest_plugins = ["pytester"]


def test_parameterized_mode(pytester):
    licenses = _collect_licenses("pytest")
    assert all(lic != "UNKNOWN" for lic in licenses.values())
    count = len(licenses)
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
