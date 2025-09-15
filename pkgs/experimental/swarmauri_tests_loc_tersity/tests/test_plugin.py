pytest_plugins = ["pytester"]


def _make_files(tmp_path):
    good = tmp_path / "good.py"
    good.write_text("print('ok')\n")
    bad = tmp_path / "bad.py"
    bad.write_text("x = 0\n" * 401)
    return tmp_path


def test_parameterized_mode(pytester):
    pkg = _make_files(pytester.mkdir("pkg"))
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_loc_tersity",
        "--loc-root",
        str(pkg),
    )
    result.assert_outcomes(passed=1, failed=1)
    assert "swarmauri_tests_loc_tersity:loc::" in result.stdout.str()


def test_aggregate_mode(pytester):
    pkg = _make_files(pytester.mkdir("pkg"))
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_loc_tersity",
        "--loc-root",
        str(pkg),
        "--loc-mode=aggregate",
    )
    result.assert_outcomes(failed=1)
    assert "bad.py has" in result.stdout.str()
