import pytest

from swarmauri_keyprovider_pkcs11 import Pkcs11KeyProvider


@pytest.mark.unit
def test_pkcs11_missing_dependency(tmp_path) -> None:
    """Instantiation should fail if pkcs11 module is unavailable."""
    if Pkcs11KeyProvider.__module__ is None:  # pragma: no cover - sanity
        pytest.skip("module not loaded")
    with pytest.raises(ImportError):
        Pkcs11KeyProvider(module_path=str(tmp_path / "lib.so"))
