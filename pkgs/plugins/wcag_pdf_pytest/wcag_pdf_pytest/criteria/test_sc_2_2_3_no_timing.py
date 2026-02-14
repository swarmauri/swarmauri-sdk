import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.2.3"
SC_TITLE = "No Timing"
SC_LEVEL = "AAA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies if any timing is used; rare in PDFs.'

@pytest.mark.wcag21
@pytest.mark.AAA
def test_sc_2_2_3_no_timing(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
