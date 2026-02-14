![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/wcag-pdf-pytest/">
        <img src="https://img.shields.io/pypi/dm/wcag-pdf-pytest" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/wcag_pdf_pytest/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/wcag_pdf_pytest.svg"/></a>
    <a href="https://pypi.org/project/wcag-pdf-pytest/">
        <img src="https://img.shields.io/pypi/pyversions/wcag-pdf-pytest" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/wcag-pdf-pytest/">
        <img src="https://img.shields.io/pypi/l/wcag-pdf-pytest" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/wcag-pdf-pytest/">
        <img src="https://img.shields.io/pypi/v/wcag-pdf-pytest?label=wcag-pdf-pytest&color=green" alt="PyPI - wcag-pdf-pytest"/></a>
</p>

---

# wcag-pdf-pytest

`wcag-pdf-pytest` is a [pytest](https://docs.pytest.org/) plugin that scaffolds WCAG 2.1
compliance testing for PDF documents. The plugin auto-generates one test per WCAG 2.1
Success Criterion (SC) that applies to PDFs, organizes them by conformance level, and
exposes CLI switches for narrowing execution to the criteria relevant to your review.

## Features
- **SC-aware test generation** &mdash; each applicable WCAG 2.1 SC ships as an individual pytest
  module with structured docstrings that document the requirement.
- **Level-based selection** &mdash; mark sets (`A`, `AA`, `AAA`) and CLI flags allow you to focus on
  the conformance tier under audit.
- **Context-aware filtering** &mdash; opt-in inclusion of "Depends" criteria lets you decide when
  to execute context-sensitive checks.
- **Extensible PDF inspection** &mdash; centralize heavy lifting in `pdf_inspector.py` so new
  assertions or document parsers can be layered in without touching the generated tests.

## Installation

### pip

```bash
pip install wcag-pdf-pytest[pdf]
```

### uv

```bash
uv add wcag-pdf-pytest[pdf]
```

Install the optional `pdf` extra when you need the bundled `pypdf` helpers.

## Usage

Run the full WCAG 2.1 test suite against a PDF document:

```bash
pytest --wcag-pdf path/to/file.pdf
```

Execute only Level AA criteria using pytest markers:

```bash
pytest -m "AA" --wcag-pdf path/to/file.pdf
```

The plugin also exposes explicit CLI options:

```bash
pytest --wcag-pdf-level AA --wcag-pdf path/to/file.pdf
pytest --wcag-pdf-include-depends --wcag-pdf path/to/file.pdf
```

Tests are namespaced under the `wcag21` marker to keep discovery isolated from other pytest
plugins. Each test is seeded with an `xfail` placeholder so you can progressively
replace the stub assertion with a concrete PDF accessibility check.

## CLI reference

| Option | Description |
| --- | --- |
| `--wcag-pdf` | Path to one or more PDF files to validate. |
| `--wcag-pdf-level {A,AA,AAA}` | Restrict execution to a specific WCAG level. |
| `--wcag-pdf-include-depends` | Execute context-dependent criteria flagged as "Depends". |

Combine CLI switches with pytest marker expressions for granular selection during CI runs.

## Extending PDF checks

Extend `wcag_pdf_pytest/pdf_inspector.py` with reusable utilities that evaluate
individual criteria. Generated tests should stay declarative &mdash; import helpers from the
inspector module to keep assertions maintainable and consistent across the suite.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
