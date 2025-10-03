import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "3.3.2"
SC_TITLE = "Labels or Instructions"
SC_LEVEL = "A"
SC_APPLICABILITY = "Applies"
SC_NOTES = 'Provide clear labels/instructions for form fields.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_3_3_2_labels_or_instructions(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
