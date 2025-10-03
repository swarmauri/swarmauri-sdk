import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "1.4.12"
SC_TITLE = "Text Spacing"
SC_LEVEL = "AA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Depends on user agent capabilities for overriding spacing; some readers do not fully support it.'

@pytest.mark.wcag21
@pytest.mark.AA
def test_sc_1_4_12_text_spacing(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
