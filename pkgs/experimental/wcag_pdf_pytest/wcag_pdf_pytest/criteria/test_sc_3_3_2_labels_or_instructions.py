import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.2"
SC_TITLE = "Labels or Instructions"
SC_LEVEL = "A"
SC_APPLICABILITY = "Applies"
SC_NOTES = "Provide clear labels/instructions for form fields."

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_3_3_2_labels_or_instructions(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 3.3.2
Title        : Labels or Instructions
Level        : A
Applicability: Applies
Notes        : Provide clear labels/instructions for form fields.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
