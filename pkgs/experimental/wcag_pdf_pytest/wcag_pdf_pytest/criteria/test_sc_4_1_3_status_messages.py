import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "4.1.3"
SC_TITLE = "Status Messages"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = "If the PDF uses scripted status messages, they must be programmatically determinable."

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_4_1_3_status_messages(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 4.1.3
Title        : Status Messages
Level        : AA
Applicability: Depends
Notes        : If the PDF uses scripted status messages, they must be programmatically determinable.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
