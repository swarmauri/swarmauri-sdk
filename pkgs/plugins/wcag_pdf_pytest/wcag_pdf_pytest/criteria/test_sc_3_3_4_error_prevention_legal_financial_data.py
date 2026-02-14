import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.4"
SC_TITLE = "Error Prevention (Legal, Financial, Data)"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies if the PDF submits important data; provide reversals/confirmations/checks.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_3_3_4_error_prevention_legal_financial_data(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
