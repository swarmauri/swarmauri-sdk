"""Basic plugin registration tests."""

import pytest

from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_certs_cfssl import CfsslCertService


@pytest.mark.unit
def test_plugin_registered() -> None:
    """Ensure CfsslCertService is registered with the DynamicBase registry."""
    registry = DynamicBase._registry.get("CertServiceBase")
    assert registry is not None
    assert registry["subtypes"]["CfsslCertService"] is CfsslCertService
