"""Integration tests for the README examples pytest plugin."""

from __future__ import annotations

pytest_plugins = ["pytester"]


README_CONTENT = """# Guide

```python
print("ok")
```

```
raise SystemError("untagged")
```

```python
# pytest: skip-example
raise RuntimeError("should not run")
```

```python
raise ValueError("boom")
```
"""


def test_parameterized_mode_runs_examples(pytester):
    pytester.makefile(".md", README=README_CONTENT)
    result = pytester.runpytest("-p", "swarmauri_tests_readme_examples")
    result.assert_outcomes(passed=1, failed=1)
    stdout = result.stdout.str()
    assert "README.md::Guide::block-4" in stdout
    assert "ValueError" in stdout


def test_aggregate_mode_collects_failures(pytester):
    pytester.makefile(".md", README=README_CONTENT)
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_readme_examples",
        "--readme-mode=aggregate",
    )
    result.assert_outcomes(failed=1)
    stdout = result.stdout.str()
    assert "swarmauri_tests_readme_examples:readme-aggregate" in stdout
    assert "ValueError" in stdout


def test_cli_languages_override(pytester):
    pytester.makefile(
        ".md",
        README="""# Examples

```pycon
>>> value = 1
>>> raise RuntimeError("pycon failure")
```
""",
    )
    result = pytester.runpytest(
        "-p",
        "swarmauri_tests_readme_examples",
        "--readme-languages=pycon",
    )
    result.assert_outcomes(failed=1)
    assert "pycon" in result.stdout.str()


def test_ini_configuration_controls_files(pytester):
    docs = pytester.mkdir("docs")
    (docs / "GUIDE.md").write_text(
        """# Docs

```python
print('guided')
```
""",
        encoding="utf-8",
    )
    pytester.makepyprojecttoml(
        """
[tool.pytest.ini_options]
readme_files = \"\"\"
    docs/GUIDE.md
\"\"\"
readme_languages = \"\"\"
    python
\"\"\"
"""
    )
    result = pytester.runpytest("-p", "swarmauri_tests_readme_examples")
    result.assert_outcomes(passed=1)


def test_missing_file_emits_warning(pytester):
    pytester.makepyprojecttoml(
        """
[tool.pytest.ini_options]
readme_files = \"\"\"
    docs/MISSING.md
\"\"\"
"""
    )
    result = pytester.runpytest("-p", "swarmauri_tests_readme_examples")
    result.assert_outcomes()
    result.stdout.fnmatch_lines(["*readme examples plugin: missing files*"])
