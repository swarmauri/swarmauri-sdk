# wcag-pdf-pytest

**Pytest plugin** for structuring WCAG 2.1 **A / AA / AAA** compliance checks against **PDF** documents.

> Ships **one test file per WCAG 2.1 Success Criterion** relevant to PDFs (the "PDF_Rules_Filtered" set). Each test is pre-marked with its **Level** and includes metadata in a docstring.

## Install (uv + Poetry backend)

This project uses a **uv-based pyproject.toml** with a **Poetry build backend**. There is **no uv.toml**; uv reads configuration and dev-dependencies from `pyproject.toml`.

```bash
uv venv -p 3.11
source .venv/bin/activate
uv pip install -e .[pdf]
```

Or with Poetry:

```bash
poetry install -E pdf
poetry run pytest -m "AA" --wcag-pdf path/to/file.pdf
```

## Usage

Run all generated WCAG 2.1 tests:

```bash
pytest --wcag-pdf path/to/file.pdf
```

Run only **AA** criteria:

```bash
pytest -m "AA" --wcag-pdf path/to/file.pdf
# or
pytest --wcag-pdf-level AA --wcag-pdf path/to/file.pdf
```

Include context-dependent criteria (**Depends**):

```bash
pytest --wcag-pdf-include-depends --wcag-pdf path/to/file.pdf
```

### CLI namespace
The plugin's options are prefixed with `--wcag-pdf-*` to avoid collisions with other pytest plugins.

### Notes
- Tests currently `xfail` as **"Implementation pending"**; next steps will add real PDF checks.
- Centralize real checks in `wcag_pdf_pytest/pdf_inspector.py`.

## License

Apache-2.0. See [LICENSE](LICENSE).
