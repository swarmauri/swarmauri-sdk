import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.1"
SC_TITLE = "Use of Color"
SC_LEVEL = "A"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Do not use color alone to convey information in PDFs.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_1_4_1___(wcag_pdf_paths, wcag_context):
    """WCAG 2.1 SC 1.4.1: Use of Color (Level A).
    Automated heuristic for static PDFs:
      - 1.3.x: Tagging presence used to infer structure/sequence; others treated N/A.
      - 1.4.x (≤1.4.9): Media presence and color ops scanned; images-of-text flagged if images exist.
    """
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
