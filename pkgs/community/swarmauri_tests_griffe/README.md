# swarmauri_tests_griffe

`swarmauri_tests_griffe` is a pytest plugin that loads project packages with
[Griffe](https://github.com/mkdocstrings/griffe) and fails the test session if
any warnings are emitted during inspection. The plugin is automatically
integrated into the Swarmauri test suite via the shared `pkgs/conftest.py` file.

## Usage

Once installed, the plugin adds a dynamic test for each configured package. By
default the current package defined in `pyproject.toml` is inspected, but you
can target additional packages with:

```bash
pytest --griffe-package other_package
```

If Griffe produces warnings while processing the package, the generated test
fails and reports the warning details.
