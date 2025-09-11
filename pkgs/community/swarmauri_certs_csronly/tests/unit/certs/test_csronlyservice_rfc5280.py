import pytest

from swarmauri_certs_csronly import CsrOnlyService


@pytest.mark.unit
def test_csronlyservice_mentions_rfc5280() -> None:
    assert "RFC 5280" in CsrOnlyService.__doc__
