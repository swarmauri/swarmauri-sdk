import pytest

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def test_invalid_jwks_structure_rfc7517() -> None:
    def bad_fetch():
        return {"k": []}

    v = CachedJWKSVerifier(fetch=bad_fetch)
    with pytest.raises(RuntimeError):
        v.refresh(force=True)
