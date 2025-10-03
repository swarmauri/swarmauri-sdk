import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.3"
SC_TITLE = "Error Suggestion"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Applies"
SC_NOTES = "Provide suggestions to correct input errors in PDF forms."

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_3_3_3_error_suggestion(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 3.3.3
Title        : Error Suggestion
Level        : AA
Applicability: Applies
Notes        : Provide suggestions to correct input errors in PDF forms.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
