import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.4"
SC_TITLE = "Resize Text"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Content remains readable up to 200% zoom without loss of content or functionality.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_4__(wcag_pdf_paths, wcag_context):
    """WCAG 2.1 SC 1.4.4: Resize Text (Level AA).
    Automated heuristic for static PDFs:
      - 1.3.x: Tagging presence used to infer structure/sequence; others treated N/A.
      - 1.4.x (≤1.4.9): Media presence and color ops scanned; images-of-text flagged if images exist.
    """
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
