import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.3.2"
SC_TITLE = "Three Flashes"
SC_LEVEL = "AAA"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies if flashing content is present.'

@pytest.mark.wcag21
@pytest.mark.AAA
def test_sc_2_3_2__(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
