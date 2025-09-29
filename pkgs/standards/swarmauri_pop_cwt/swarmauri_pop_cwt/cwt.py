from __future__ import annotations

import base64
import cbor2
from typing import Mapping, Optional

from cose.algorithms import SignatureAlg
from cose.exceptions import CoseException
from cose.headers import Algorithm, KID
from cose.keys import CoseKey
from cose.keys.keyparam import (
    EC2KpCurve,
    EC2KpX,
    EC2KpY,
    KpKty,
    OKPKpCurve,
    OKPKpX,
    RSAKpE,
    RSAKpN,
)
from cose.keys.keytype import KtyEC2, KtyOKP, KtyRSA
from cose.messages import Sign1Message

from swarmauri_core.pop import (
    BindType,
    CnfBinding,
    Feature,
    PoPBindingError,
    PoPParseError,
    PoPVerificationError,
    PoPKind,
)
from swarmauri_base.pop import (
    PopSignerBase,
    PopVerifierBase,
    RequestContext,
    sha256_b64u,
)


def _b64u_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _ensure_cose_key(key_obj) -> CoseKey:
    if isinstance(key_obj, CoseKey):
        return key_obj
    if isinstance(key_obj, Mapping):
        return CoseKey.from_dict(dict(key_obj))
    raise TypeError("COSE key must be a CoseKey or mapping")


def _compute_cose_thumbprint(key: CoseKey) -> str:
    kty = key[KpKty]
    if kty == KtyOKP:
        fields = {
            1: kty.identifier,
            -1: key[OKPKpCurve].identifier,
            -2: key[OKPKpX],
        }
    elif kty == KtyEC2:
        fields = {
            1: kty.identifier,
            -1: key[EC2KpCurve].identifier,
            -2: key[EC2KpX],
            -3: key[EC2KpY],
        }
    elif kty == KtyRSA:
        fields = {
            1: kty.identifier,
            -1: key[RSAKpN],
            -2: key[RSAKpE],
        }
    else:
        raise PoPParseError("Unsupported COSE key type for thumbprint")
    canonical = cbor2.dumps(fields, canonical=True)
    return sha256_b64u(canonical)


def _alg_name(alg_obj: SignatureAlg) -> str:
    return alg_obj.name if hasattr(alg_obj, "name") else str(alg_obj)


class CwtPoPVerifier(PopVerifierBase):
    """Verifier for COSE Sign1-based PoP proofs."""

    def __init__(self) -> None:
        super().__init__(
            kind=PoPKind.CWT,
            header_name="CWP",
            features=Feature.NONCE | Feature.REPLAY | Feature.ATH,
            algorithms=("ES256", "EdDSA", "PS256"),
        )

    async def _verify_core(
        self,
        proof: str,
        context: RequestContext,
        cnf: CnfBinding,
        *,
        replay,
        keys,
        extras,
    ) -> None:
        self._enforce_bind_type(cnf, context.policy, expected=BindType.COSE_THUMB)

        try:
            sign1 = Sign1Message.decode(_b64u_decode(proof))
        except (ValueError, CoseException) as exc:
            raise PoPParseError("Invalid CWT PoP payload") from exc

        alg_obj = sign1.phdr.get(Algorithm)
        if alg_obj is None:
            raise PoPParseError("COSE message missing algorithm header")
        alg_name = _alg_name(alg_obj)
        self._enforce_alg_policy(alg_name, context.policy)

        key_obj = extras.get("public_cose_key")
        if key_obj is None and keys is not None:
            kid = sign1.phdr.get(KID)
            resolved = None
            if kid is not None:
                resolved = keys.by_kid(bytes(kid))
            if resolved is None:
                resolved = keys.by_thumb(cnf)
            key_obj = resolved
        if key_obj is None:
            raise PoPVerificationError("Verification key unavailable for CWT PoP")

        try:
            cose_key = _ensure_cose_key(key_obj)
        except Exception as exc:  # noqa: BLE001
            raise PoPParseError("Unsupported COSE key format") from exc

        thumb = _compute_cose_thumbprint(cose_key)
        if thumb != cnf.value_b64u:
            raise PoPBindingError("COSE key thumbprint does not match access token cnf")

        sign1.key = cose_key
        try:
            if not sign1.verify_signature():
                raise PoPVerificationError("COSE signature verification failed")
        except CoseException as exc:
            raise PoPVerificationError("COSE signature verification failed") from exc

        try:
            claims = cbor2.loads(sign1.payload)
        except (ValueError, TypeError) as exc:
            raise PoPParseError("CWT PoP payload is not valid CBOR") from exc

        if claims.get("htm") != context.method or claims.get("htu") != context.htu:
            raise PoPVerificationError("CWT htm/htu mismatch")

        try:
            iat = int(claims["iat"])
        except (KeyError, ValueError, TypeError) as exc:
            raise PoPParseError("Invalid or missing iat claim") from exc
        self._validate_iat(iat, context.policy)

        jti = claims.get("jti")
        if not isinstance(jti, str) or not jti:
            raise PoPParseError("Missing jti claim")

        nonce_expected = extras.get("nonce")
        nonce_claim = claims.get("nonce")
        if nonce_expected is not None and nonce_claim != nonce_expected:
            raise PoPVerificationError("Nonce mismatch")

        ath_claim = claims.get("ath")
        if context.policy.require_ath:
            self._require_ath(ath_claim=ath_claim, policy=context.policy, extras=extras)
        elif ath_claim and "access_token" in extras:
            expected_ath = self._compute_ath(extras["access_token"])
            if expected_ath != ath_claim:
                raise PoPVerificationError(
                    "ath claim does not match provided access token"
                )

        replay_scope = f"cwt:{context.htu}"
        self._check_replay(
            replay=replay,
            scope=replay_scope,
            key=jti,
            ttl_s=context.policy.max_skew_s,
        )


class CwtPoPSigner(PopSignerBase):
    """Signer that emits COSE Sign1 PoP proofs."""

    def __init__(
        self,
        *,
        private_key,
        public_key,
        algorithm: SignatureAlg,
        include_query: bool = False,
    ) -> None:
        super().__init__(
            kind=PoPKind.CWT, header_name="CWP", include_query=include_query
        )
        self._private_key = _ensure_cose_key(private_key)
        self._public_key = _ensure_cose_key(public_key)
        self._algorithm = algorithm
        self._thumbprint = _compute_cose_thumbprint(self._public_key)

    def cnf_binding(self) -> CnfBinding:
        return CnfBinding(BindType.COSE_THUMB, self._thumbprint)

    def sign_request(
        self,
        method: str,
        url: str,
        *,
        kid: Optional[bytes] = None,
        jti: Optional[str] = None,
        ath_b64u: Optional[str] = None,
        extra_claims: Mapping[str, object] | None = None,
    ) -> str:
        claims = self._base_claims(method, url, jti=jti, ath_b64u=ath_b64u)
        payload_map = self._merge_claims(claims, extra_claims)
        payload_bytes = cbor2.dumps(payload_map, canonical=True)

        headers = {Algorithm: self._algorithm}
        if kid is not None:
            headers[KID] = kid

        msg = Sign1Message(phdr=headers, uhdr={}, payload=payload_bytes)
        msg.key = self._private_key
        encoded = msg.encode()
        return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode("ascii")
