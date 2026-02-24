# STYLE_GUIDE — wcag-pdf-pytest

## Markers (required)

Use uppercase WCAG level markers on every test:

- `@pytest.mark.A`
- `@pytest.mark.AA`
- `@pytest.mark.AAA`

Select by level using standard pytest marker expressions:

```bash
pytest -m "AA" --wcag-pdf path/to/file.pdf
```

The plugin also accepts `--wcag-pdf-level A|AA|AAA` for narrowing.

## One SC per file

Place files in `src/wcag_pdf_pytest/criteria/` using this pattern:

```
test_sc_<number_with_underscores>_<slug_of_title>.py
```

**Each file contains one test** and must include a docstring with these fields:

- **WCAG 2.1 SC number**
- **Title**
- **Level** (`A`, `AA`, `AAA`)
- **Applicability** (`Applies`, `Depends`, `Typically N/A`)
- **Applicability notes**

Example:

```python
import pytest

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_3_contrast_minimum(wcag_pdf_paths, wcag_context):
    """
    WCAG 2.1 Success Criterion
    Number       : 1.4.3
    Title        : Contrast (Minimum)
    Level        : AA
    Applicability: Applies
    Notes        : Text and images of text in PDFs should meet minimum contrast ratios.
    """
    # Implement using evaluate_sc in pdf_inspector.py
```

## Fixtures & CLI

- `wcag_pdf_paths`: list of PDFs from `--wcag-pdf`.
- `wcag_context.include_depends`: set with `--wcag-pdf-include-depends` to enforce context-dependent criteria.
- Narrow by level using pytest markers (`-m "AA"`) or `--wcag-pdf-level AA`.

## Implementation Guidance

- Keep test functions declarative; put heavy logic in `pdf_inspector.py`.
- Avoid backward-compatibility shims; target Python 3.9+ (prefer 3.11+).
- Use deterministic names and marker usage to enable selective runs and reporting.
