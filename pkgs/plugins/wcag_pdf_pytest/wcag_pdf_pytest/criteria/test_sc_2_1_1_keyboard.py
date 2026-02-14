import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "2.1.1"
SC_TITLE = "Keyboard"
SC_LEVEL = "A"
SC_APPLICABILITY = "Depends"
SC_NOTES = 'Applies for interactive PDF content; all functionality should be operable via keyboard.'

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_2_1_1_keyboard(wcag_pdf_paths, wcag_context):
    assert wcag_pdf_paths, "No --wcag-pdf provided."
    res = evaluate_sc(SC_NUM, SC_TITLE, SC_LEVEL, wcag_pdf_paths, SC_APPLICABILITY, SC_NOTES)
    assert isinstance(res, SCResult)
    assert res.passed, res.reason
