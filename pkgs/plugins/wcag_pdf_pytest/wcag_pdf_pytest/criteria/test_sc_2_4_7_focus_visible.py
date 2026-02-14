import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.4.7"
SC_TITLE = "Focus Visible"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'For interactive content, provide a visible focus indicator.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_2_4_7__(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
