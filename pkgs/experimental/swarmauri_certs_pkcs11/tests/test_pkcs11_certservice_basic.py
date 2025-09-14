import pytest

pytest.importorskip("pkcs11")

from swarmauri_certs_pkcs11 import Pkcs11CertService


@pytest.mark.test
@pytest.mark.unit
def test_supports_lists_features() -> None:
    svc = Pkcs11CertService(module_path="/usr/lib/softhsm/libsofthsm2.so")
    caps = svc.supports()
    assert "csr" in caps["features"]
