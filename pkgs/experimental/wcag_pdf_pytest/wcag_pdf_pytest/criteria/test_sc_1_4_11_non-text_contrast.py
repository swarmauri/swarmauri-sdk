import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.11"
SC_TITLE = "Non-text Contrast"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Applies"
SC_NOTES = "UI components and graphical objects (e.g., form controls) must meet 3:1 contrast."

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_11_non-text_contrast(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 1.4.11
Title        : Non-text Contrast
Level        : AA
Applicability: Applies
Notes        : UI components and graphical objects (e.g., form controls) must meet 3:1 contrast.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
