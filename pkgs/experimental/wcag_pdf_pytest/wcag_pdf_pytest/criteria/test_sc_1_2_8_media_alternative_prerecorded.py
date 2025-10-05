import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.2.8"
SC_TITLE = "Media Alternative (Prerecorded)"
SC_LEVEL = "AAA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Relevant only if the PDF embeds prerecorded media.'

@pytest.mark.wcag21
@pytest.mark.AAA
def test_sc_1_2_8___(wcag_pdf_paths):
    """WCAG 2.1 SC 1.2.8: Media Alternative (Prerecorded) (Level AAA).
    This test uses a lightweight heuristic implementation:
      - 1.1.x: Passes if no images are present; if images exist, requires '/Alt' entries.
      - 1.2.x: Passes if no time-based media is present (N/A); otherwise fails.
    """
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
