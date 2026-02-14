import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.1"
SC_TITLE = "Error Identification"
SC_LEVEL = "A"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Identify input errors in PDF forms.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_3_3_1_error_identification(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
