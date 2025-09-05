import pytest

from swarmauri_base.certs import CertServiceBase


@pytest.mark.unit
def test_certservicebase_mentions_rfc2986() -> None:
    assert "RFC 2986" in CertServiceBase.__doc__
