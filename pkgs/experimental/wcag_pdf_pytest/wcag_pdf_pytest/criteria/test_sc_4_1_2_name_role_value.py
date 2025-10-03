import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "4.1.2"
SC_TITLE = "Name, Role, Value"
SC_LEVEL = "A"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'For interactive controls, expose name/role/state programmatically via tagging.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_4_1_2_name_role_value(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
