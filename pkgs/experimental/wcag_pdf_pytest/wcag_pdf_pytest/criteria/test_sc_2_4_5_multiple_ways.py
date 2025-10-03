import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.4.5"
SC_TITLE = "Multiple Ways"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies when PDFs are part of a set; provide more than one way to locate content.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_2_4_5__(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
