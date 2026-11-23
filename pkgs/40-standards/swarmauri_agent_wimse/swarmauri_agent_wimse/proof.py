"""WIMSE wire checks for the pinned research interop profile."""

from base64 import b64encode, urlsafe_b64encode
from hashlib import sha256
from math import isfinite
from secrets import token_urlsafe
from threading import Lock
from time import time

from tba_concrete_jwt import decode_jwt_unverified
from tba_profile_workload_credential_wimse_wit import verify_wit
from tba_profile_workload_proof_wimse_http_signature.request import (
    FIELDS,
    _authenticate_signature,
)
from tba_provider_jose_cryptography.jws import sign_compact_jwt
from tba_provider_jose_cryptography.public_jws import verify_public_jws


def digest(token):
    return (
        urlsafe_b64encode(sha256(token.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )


class Rejected(ValueError):
    def __init__(self, status, reason):
        super().__init__(reason)
        self.status = status


class ReplayCache:
    """In-process replay protection for one endpoint worker."""

    def __init__(self):
        self._entries = {}
        self._lock = Lock()

    def check_and_store(self, key, *, now, ttl_s):
        with self._lock:
            self._entries = {
                key: exp for key, exp in self._entries.items() if exp > now
            }
            if key in self._entries:
                return False
            self._entries[key] = now + ttl_s
            return True


def headers_dict(pairs):
    headers = {}
    protected = {
        "authorization",
        "content-type",
        "content-digest",
        "signature",
        "signature-input",
        "txn-token",
        "workload-identity-token",
    }
    for name, value in pairs:
        key = name.lower()
        if key in headers and key in protected:
            raise Rejected(400, "ambiguous-security-header")
        headers[key] = value
    return headers


def verify_http(method, target, headers, body, *, audience, trust, replay):
    expected = (
        "sha-256=:" + b64encode(sha256(body).digest()).decode("ascii") + ":"
    )
    if (
        headers.get("content-digest") != expected
        or headers.get("content-type") != "application/json"
    ):
        raise Rejected(401, "request-digest-invalid")
    try:
        return _authenticate_signature(
            tuple(headers.items()),
            method=method,
            path=target,
            now=int(time()),
            trust_by_domain=trust,
            replay_store=replay,
            verify_credential=verify_wit,
            authority=None,
            derived=FIELDS,
            binding="wimse-aud",
            expected_binding=audience,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise Rejected(401, "wimse-proof-invalid") from exc


def verify_workload_transaction(token, *, keys, issuer, audience, workload):
    """Verify the issuer, lifetime, and workload binding of a transaction."""
    try:
        decoded = decode_jwt_unverified(token)
        headers, claims = decoded.jws.protected_headers, decoded.claims
        if (
            headers["typ"] != "txntoken+jwt"
            or claims["iss"] != issuer
            or claims["aud"] != audience
        ):
            raise ValueError("transaction issuer, type or audience")
        (key,) = [key for key in keys if key["kid"] == headers["kid"]]
        verify_public_jws(token, key)
        iat, exp = claims["iat"], claims["exp"]
        if (
            not all(
                type(value) in (int, float) and isfinite(value)
                for value in (iat, exp)
            )
            or not iat <= time() < exp
        ):
            raise ValueError("transaction validity")
        if (
            claims["req_wl"] != workload
            or not claims["txn"]
            or not claims["sub"]
        ):
            raise ValueError("transaction binding")
        return claims
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise Rejected(403, "transaction-not-authorized") from exc


def verify_transaction(token, *, keys, issuer, audience, workload, file):
    """Verify that the transaction permits reading the requested file."""
    claims = verify_workload_transaction(
        token, keys=keys, issuer=issuer, audience=audience, workload=workload
    )
    try:
        if (
            "files:read" not in claims["scope"].split()
            or claims["tctx"]["file"] != file
        ):
            raise ValueError("transaction file binding")
        return claims
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise Rejected(403, "transaction-not-authorized") from exc


def produce_wpt(wit, token, *, audience, signer, key_reference):
    # The B_CHAIN profile compares the exact configured audience. Preserve
    # its bare origin on the wire rather than normalizing a slash into it.
    key = decode_jwt_unverified(wit).claims["cnf"]["jwk"]
    proof = sign_compact_jwt(
        signer,
        {
            "aud": audience,
            "exp": int(time()) + 60,
            "jti": token_urlsafe(24),
            "wth": digest(wit),
            "tth": digest(token),
        },
        headers={"typ": "wpt+jwt", "alg": key["alg"]},
        key_reference=key_reference,
    )
    verify_public_jws(proof, key)
    return {
        "Workload-Identity-Token": wit,
        "Txn-Token": token,
        "Authorization": f"WPT {proof}",
    }


def verify_wpt(headers, *, audience, trust, replay):
    now = int(time())
    try:
        wit = headers["workload-identity-token"]
        identity = verify_wit(wit, trust_by_domain=trust, now=now).claims
        key = identity["cnf"]["jwk"]
        scheme, proof = headers["authorization"].split(" ", 1)
        if scheme.lower() != "wpt":
            raise ValueError("missing WPT")
        decoded = decode_jwt_unverified(proof)
        jose, claims = decoded.jws.protected_headers, decoded.claims
        if jose["typ"] != "wpt+jwt" or jose["alg"] != key["alg"]:
            raise ValueError("invalid WPT protected header")
        verify_public_jws(proof, key)
        expires, nonce = claims["exp"], claims["jti"]
        if (
            claims["aud"] != audience
            or type(expires) not in (int, float)
            or not now < expires <= now + 300
            or not isinstance(nonce, str)
            or not nonce
            or claims["wth"] != digest(wit)
            or claims["tth"] != digest(headers["txn-token"])
        ):
            raise ValueError("invalid WPT claims")
        if not replay.check_and_store(
            ("wpt", identity["sub"], nonce), now=now, ttl_s=expires - now
        ):
            raise ValueError("proof replay")
        return identity["sub"]
    except (KeyError, TypeError, ValueError) as exc:
        raise Rejected(401, "wimse-proof-invalid") from exc
