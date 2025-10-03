import pytest
from wcag_pdf_pytest.pdf_inspector import evaluate_sc, SCResult

SC_NUM = "4.1.2"
SC_TITLE = "Name, Role, Value"
SC_LEVEL = "A"
SC_APPLICABILITY = "Depends"
SC_NOTES = "For interactive controls, expose name/role/state programmatically via tagging."

@pytest.mark.wcag21
@pytest.mark.A
def test_sc_4_1_2_name_role_value(wcag_pdf_paths, wcag_context):
    """
WCAG 2.1 Success Criterion
Number       : 4.1.2
Title        : Name, Role, Value
Level        : A
Applicability: Depends
Notes        : For interactive controls, expose name/role/state programmatically via tagging.
"""

    if not wcag_pdf_paths:
        pytest.skip("No --wcag-pdf provided. Pass one or more PDFs via --wcag-pdf <path>.")

    if SC_APPLICABILITY == "Depends" and not wcag_context.include_depends:
        pytest.xfail("Context-dependent criterion: run with --wcag-pdf-include-depends to enforce.")

    # Placeholder for real evaluation (to be implemented in phases).
    pytest.xfail(f"Implementation pending for {SC_NUM} – {SC_TITLE} (Level {SC_LEVEL}).")
