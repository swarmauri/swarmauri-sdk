import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.3"
SC_TITLE = "Error Suggestion"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Provide suggestions to correct input errors in PDF forms.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_3_3_3_error_suggestion(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
