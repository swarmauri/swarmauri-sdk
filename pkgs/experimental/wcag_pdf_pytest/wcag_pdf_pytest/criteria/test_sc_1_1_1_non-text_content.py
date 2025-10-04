import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.1.1"
SC_TITLE = "Non-text Content"
SC_LEVEL = "A"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Provide text alternatives for images and other non-text content in tagged PDFs.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_1_1_1__(wcag_pdf_paths):
    """WCAG 2.1 SC 1.1.1: Non-text Content (Level A).
    This test uses a lightweight heuristic implementation:
      - 1.1.x: Passes if no images are present; if images exist, requires '/Alt' entries.
      - 1.2.x: Passes if no time-based media is present (N/A); otherwise fails.
    """
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
