"""RFC 7517 - JSON Web Key (JWK) utilities using swarmauri key providers."""

from __future__ import annotations

from typing import Final

from .runtime_cfg import settings

RFC7517_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7517"

_KID = "rsa1"
_RSA_N = (
    "pTD0Z0UkLWQUM2dNvDcOIR0zgzbJI8kY0GKx_U1DoY9uRXIbHqDO_JPsMXEEo0qIHaQ3wNxydqXT7D-"
    "oLocEa7iEjULDKj5PLGBr8D2rdQ1Tue13m2q16YeNjQ3LZwNwvoX6li6EsQk04CIjLqrx7aIwvlyFe2cBA"
    "ojBBANxA0ZxKYMRrPKNpn3rD5FOWYqeLrMWi50c94hrWP-oKnLF_7BKfvioeERoQ6WAgqHLGjQ8Wg0VIEr9"
    "5i0E208uWUJFskF3-qsle_HFj23KTG2MAwqZtxnpk600Hdko7gR8Rs_3cCok2YFOPgN78k3tzJZtqgZ7ikp"
    "pUcsYok5fcWIDwQ"
)
_RSA_E = "AQAB"
_RSA_D = (
    "CGrfsVl1F_kHDH2BmQsnJanSw6dphXDMWmYFEta6kQN5h4Fif2OLWJSDDxvmtBlqqTQCgUnabVBS5bFytPg"
    "9Ue3jlz0lK8RkDWtWZLYHxB2rPAitNRaxcVZucJcY28Vxm8vA8qEpMso4zwj-SPT-AfFnUXPue1TK2OG2ECn"
    "KuvNpfjHXda4giyOtiO5k5ayv7qcYfEEdbFAdoVwAIMM1ooVUEwj6Ek9iKeSzZ6VRBeD6__c9m_DEacfoVVad"
    "b7Jq01dZK5iZqy2t9ORyIQRSqkL87s3BrSr9oVFmsX69tMdlXcdubXDdjEZkDrwojLjn2mfo32m9lf8vSkyr3"
    "Ch9xw"
)
_RSA_P = (
    "0-HFTeqZdtpKoRB6-pX352BU2MNlfSe6uZT4Owp7ZmlAEyyMkWpttZHp3CIjt3VFKwoSc4q1DDRZ_GnHjXOX"
    "iv7o7ewkm7OtbOg7T5z0fMDtEAEj89hiOr29tSCT0aO1A5wj-kcQykTiqlZSjKXgtBTzvN7X3wv_j9C1aMctLBM"
)
_RSA_Q = (
    "x5Zd7hxz-pr4BNem6u26h6Kh64BEEU9Id4Hmu4apkr1Evl2mEuR8Kq5ycvG0Vnmo-RexiCiCttFEl-PyM130b"
    "zX1RBxD00awHgrcPLXNBlIzrV9wAFD0hOhxAIQ8j9f0CYwiXFU-a5XIrLohYVBM45r-fFXtMXv4vaMvFhuYY1s"
)
_RSA_DP = (
    "KcOY1pDliw3gI_tRok8pPEw6rTdmq9LG9YmtnEWmqTsZzC29z3QBCAco56E7FRBif-dOV8QBh9RR4HUhRnqAZn"
    "90fmFLnf0-s_baqgiwEF8e20a-RXRjeFyqJiezu2Dfb0S5ur2DS7tkSlsVjm-r6RMwMAxk1KxSxZBIEc0g1E0"
)
_RSA_DQ = (
    "ZsxI5upaxhnpYr0cKOZ264NVeLGg3XWDcqJCkBXE42J-tLoRXqu2VFlzc0aQxvV0lY-hjeqnoLfaZ40tY02iJ2"
    "GYSRNxz7EZ5u9bDh3pUrcmDMcaLd-Egawi_8wcUU4-UGiQDhSNyOXl7SkVJkUwxQ5AwxOSzqj2rd4N04o1C_8"
)
_RSA_QI = (
    "FYscIZgU1Q8ZBdupkxujMmb9ja0o0XMH7GeVMQzO1mjgCcrzfAbOlM27mfNd4aAqzOEGQg5_AcqQkgfNODw9NZI"
    "uxGYbFHGIB1pUf7JBF-KCctKYLVc5PAVmNGdpPZ0q82awgNk4rJB-Ypdz1EEz0tOZihn4VO-dsCONbwMf0yU"
)

_PRIVATE_JWK = {
    "kty": "RSA",
    "alg": "RS256",
    "use": "sig",
    "kid": _KID,
    "n": _RSA_N,
    "e": _RSA_E,
    "d": _RSA_D,
    "p": _RSA_P,
    "q": _RSA_Q,
    "dp": _RSA_DP,
    "dq": _RSA_DQ,
    "qi": _RSA_QI,
}

_PUBLIC_JWK = {k: _PRIVATE_JWK[k] for k in ("kty", "alg", "use", "kid", "n", "e")}


def load_signing_jwk() -> dict:
    """Return the private RSA signing key as a JWK mapping."""
    if not settings.enable_rfc7517:
        raise RuntimeError(f"RFC 7517 support disabled: {RFC7517_SPEC_URL}")
    return _PRIVATE_JWK.copy()


def load_public_jwk() -> dict:
    """Return the public RSA key as a JWK mapping."""
    if not settings.enable_rfc7517:
        raise RuntimeError(f"RFC 7517 support disabled: {RFC7517_SPEC_URL}")
    return _PUBLIC_JWK.copy()


__all__ = ["load_signing_jwk", "load_public_jwk", "RFC7517_SPEC_URL"]
