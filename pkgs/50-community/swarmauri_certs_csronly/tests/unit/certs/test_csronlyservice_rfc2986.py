import pytest

from swarmauri_certs_csronly import CsrOnlyService


@pytest.mark.unit
def test_csronlyservice_mentions_rfc2986() -> None:
    assert "RFC 2986" in CsrOnlyService.__doc__
