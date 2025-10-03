import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.12"
SC_TITLE = "Text Spacing"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = "Depends on user agent capabilities for overriding spacing; some readers do not fully support it."

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_12_text_spacing(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 1.4.12
Title        : Text Spacing
Level        : AA
Applicability: Depends
Notes        : Depends on user agent capabilities for overriding spacing; some readers do not fully support it.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
