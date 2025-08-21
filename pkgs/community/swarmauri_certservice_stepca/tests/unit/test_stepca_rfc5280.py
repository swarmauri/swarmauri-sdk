import pytest

from swarmauri_certservice_stepca import StepCaCertService


@pytest.mark.unit
def test_docstring_mentions_rfc5280() -> None:
    assert "RFC 5280" in StepCaCertService.__doc__
