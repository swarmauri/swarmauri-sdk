import pytest

from swarmauri_tokens_jwt import (
    JWTClaimsValidationError,
    JWTClaimsValidator,
)


@pytest.mark.unit
def test_validates_registered_claims_and_policy() -> None:
    validator = JWTClaimsValidator(
        required_claims={"sub", "iat", "exp"},
        issuer="issuer",
        audience="api",
        required_scopes={"documents:read"},
        required_roles={"member"},
    )

    claims = validator.validate(
        {
            "sub": "alice",
            "iat": 90,
            "nbf": 90,
            "exp": 110,
            "iss": "issuer",
            "aud": ["api", "other"],
            "scope": "documents:read profile",
            "roles": ["member"],
        },
        now=100,
    )

    assert claims["sub"] == "alice"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("claims", "message"),
    [
        ({"iat": 90, "exp": 110}, "Missing required claims: sub"),
        ({"sub": "a", "iat": 90, "exp": 100}, "Token has expired"),
        (
            {"sub": "a", "iat": 90, "exp": 110, "nbf": 101},
            "Token is not yet valid",
        ),
        (
            {"sub": "a", "iat": 101, "exp": 110},
            "Token was issued in the future",
        ),
    ],
)
def test_rejects_invalid_required_and_temporal_claims(
    claims: dict[str, object], message: str
) -> None:
    validator = JWTClaimsValidator(required_claims={"sub", "iat", "exp"})

    with pytest.raises(JWTClaimsValidationError, match=message):
        validator.validate(claims, now=100)


@pytest.mark.unit
def test_rejects_issuer_audience_scope_and_role_policy() -> None:
    base = {"iss": "wrong", "aud": "other", "scope": "read", "roles": []}

    with pytest.raises(JWTClaimsValidationError, match="issuer"):
        JWTClaimsValidator(issuer="issuer").validate(base, now=100)
    with pytest.raises(JWTClaimsValidationError, match="audience"):
        JWTClaimsValidator(audience="api").validate(base, now=100)
    with pytest.raises(JWTClaimsValidationError, match="scopes: write"):
        JWTClaimsValidator(required_scopes={"write"}).validate(base, now=100)
    with pytest.raises(JWTClaimsValidationError, match="roles: member"):
        JWTClaimsValidator(required_roles={"member"}).validate(base, now=100)


@pytest.mark.unit
def test_custom_claim_hook_is_extensible() -> None:
    class TenantValidator(JWTClaimsValidator):
        def validate_custom_claims(self, claims):
            if claims.get("tenant") != "allowed":
                raise JWTClaimsValidationError("Invalid tenant")

    with pytest.raises(JWTClaimsValidationError, match="tenant"):
        TenantValidator().validate({"tenant": "denied"}, now=100)
