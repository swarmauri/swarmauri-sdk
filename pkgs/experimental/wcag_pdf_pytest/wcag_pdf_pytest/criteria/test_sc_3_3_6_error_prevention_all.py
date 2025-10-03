import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.6"
SC_TITLE = "Error Prevention (All)"
SC_LEVEL = "AAA"
SC_APPLICABILITY = "Applies"
SC_NOTES = "Prevent errors in all forms where possible."

@pytest.mark.wcag21
@pytest.mark.AAA
def test_sc_3_3_6_error_prevention_all(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 3.3.6
Title        : Error Prevention (All)
Level        : AAA
Applicability: Applies
Notes        : Prevent errors in all forms where possible.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
