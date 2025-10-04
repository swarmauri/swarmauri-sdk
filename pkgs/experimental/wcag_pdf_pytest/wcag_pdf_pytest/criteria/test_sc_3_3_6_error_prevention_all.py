import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.6"
SC_TITLE = "Error Prevention (All)"
SC_LEVEL = "AAA"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Prevent errors in all forms where possible.'

@pytest.mark.wcag21
@pytest.mark.AAA
def test_sc_3_3_6_error_prevention_all(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
