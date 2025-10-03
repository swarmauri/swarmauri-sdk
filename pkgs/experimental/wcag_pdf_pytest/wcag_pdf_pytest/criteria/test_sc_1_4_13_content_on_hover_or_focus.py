import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.13"
SC_TITLE = "Content on Hover or Focus"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = "Relevant if the PDF uses interactive widgets or tooltips."

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_13_content_on_hover_or_focus(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 1.4.13
Title        : Content on Hover or Focus
Level        : AA
Applicability: Depends
Notes        : Relevant if the PDF uses interactive widgets or tooltips.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
