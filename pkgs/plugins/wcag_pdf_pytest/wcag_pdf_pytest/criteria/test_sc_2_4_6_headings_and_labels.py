import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.4.6"
SC_TITLE = "Headings and Labels"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Use clear headings and form labels in tagged PDFs.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_2_4_6___(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
