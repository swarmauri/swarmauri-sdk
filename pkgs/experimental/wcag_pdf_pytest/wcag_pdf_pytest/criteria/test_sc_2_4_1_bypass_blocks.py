import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.4.1"
SC_TITLE = "Bypass Blocks"
SC_LEVEL = "A"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies to sets of documents or PDFs with repeated blocks (e.g., template-based front matter).'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_2_4_1__(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
