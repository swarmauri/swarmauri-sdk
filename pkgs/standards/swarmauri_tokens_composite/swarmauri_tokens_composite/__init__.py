from __future__ import annotations

import base64
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Literal

try:  # pragma: no cover - allow running without core/base packages
    from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
except Exception:  # pragma: no cover

    class TokenServiceBase:  # minimal stub
        pass


try:  # pragma: no cover
    from swarmauri_core.tokens.ITokenService import ITokenService
except Exception:  # pragma: no cover

    class ITokenService:  # minimal stub
        pass


def _b64u_decode(s: str) -> bytes:
    # base64url without padding
    s = s + "==="[(4 - len(s) % 4) % 4 :]
    return base64.urlsafe_b64decode(s.encode("ascii"))


def _peek_jwt_parts(token: str) -> Tuple[Optional[dict], Optional[dict]]:
    """Return the unverified header and payload for a compact JWT/JWS.

    Parsing is performed manually via base64url decoding so that the
    implementation does not rely on the external ``PyJWT`` package.  Any
    parsing error results in ``(None, None)``.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None, None
        hdr = json.loads(_b64u_decode(parts[0]).decode("utf-8"))
        body = json.loads(_b64u_decode(parts[1]).decode("utf-8"))
        return hdr, body
    except Exception:
        return None, None


class CompositeTokenService(TokenServiceBase):
    """
    Route token mint/verify to one of several ITokenService implementations.

    Routing rules (in order of preference):
    ---------------------------------------
    MINT:
      1) If headers['typ'] matches a service 'formats' entry (e.g., "JWT", "SSH-CERT", "paseto"),
         pick that service.
      2) If claims['cnf'] contains 'x5t#S256' -> use mTLS-bound service (if registered).
         If contains 'jkt' -> use DPoP-bound service (if registered).
      3) If alg looks SSH-ish ('ssh-' prefix), choose an SSH-CERT service.
      4) Otherwise, choose a service that supports the requested 'alg' and includes "JWT" format.
         If multiple match, prefer the first registered.

      (Optional override) You may also pass headers['svc'] = <service_name> (its .type value)
      to force a particular service.

    VERIFY:
      1) SSH certificate line (starts with 'ssh-' and contains '-cert-') -> SSH-CERT service.
      2) If JWT-like (two dots present), peek header/payload:
          - If cnf.x5t#S256 present -> mTLS-bound service.
          - If cnf.jkt present -> DPoP-bound service.
          - Else -> plain JWT service.
      3) Otherwise, try each service in order until one succeeds (last resort).

    JWKS:
      - Union of all child services' JWKS; de-duplicate by 'kid'.

    Notes:
      - This class does NOT do background refresh; it simply delegates synchronously.
      - Child services must implement the same async interface.
    """

    type: Literal["CompositeTokenService"] = "CompositeTokenService"

    def __init__(self, services: List[ITokenService]) -> None:
        super().__init__()
        if not services:
            raise ValueError(
                "CompositeTokenService requires at least one child service"
            )
        self._services: List[ITokenService] = services

        # Precompute light capability maps
        self._by_format: Dict[str, List[ITokenService]] = {}
        self._by_alg: Dict[str, List[ITokenService]] = {}
        for svc in services:
            caps = svc.supports() or {}
            for fmt in caps.get("formats", ()):  # type: ignore[arg-type]
                self._by_format.setdefault(str(fmt).upper(), []).append(svc)
            for alg in caps.get("algs", ()):  # type: ignore[arg-type]
                self._by_alg.setdefault(str(alg).upper(), []).append(svc)

        # Common names we might special-case
        self._fmt_jwt = "JWT"
        self._fmt_ssh = "SSH-CERT"

    # ---------- capabilities ----------
    def supports(self) -> Mapping[str, Iterable[str]]:
        fmts: List[str] = []
        algs: List[str] = []
        for svc in self._services:
            caps = svc.supports() or {}
            fmts.extend([str(f) for f in caps.get("formats", ())])
            algs.extend([str(a) for a in caps.get("algs", ())])

        def _uniq(seq: List[str]) -> List[str]:
            seen = set()
            out: List[str] = []
            for x in seq:
                k = x.upper()
                if k in seen:
                    continue
                seen.add(k)
                out.append(x)
            return out

        return {"formats": _uniq(fmts), "algs": _uniq(algs)}

    # ---------- mint ----------
    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | List[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        svc = self._select_service_for_mint(claims, alg, headers)
        return await svc.mint(
            claims,
            alg=alg,
            kid=kid,
            key_version=key_version,
            headers=headers,
            lifetime_s=lifetime_s,
            issuer=issuer,
            subject=subject,
            audience=audience,
            scope=scope,
        )

    def _select_service_for_mint(
        self,
        claims: Dict[str, Any],
        alg: str,
        headers: Optional[Dict[str, Any]],
    ) -> ITokenService:
        # 0) Explicit override via header 'svc' (service type name)
        svc_hint = (headers or {}).get("svc")
        if isinstance(svc_hint, str):
            for svc in self._services:
                if getattr(svc, "type", None) == svc_hint:
                    return svc

        # 1) Header 'typ' → by format
        typ = (headers or {}).get("typ")
        if isinstance(typ, str):
            byfmt = self._by_format.get(typ.upper())
            if byfmt:
                return byfmt[0]

        # 2) cnf hints for bound JWT variants
        cnf = claims.get("cnf") if isinstance(claims, dict) else None
        if isinstance(cnf, dict):
            if "x5t#S256" in cnf:  # mTLS binding
                byfmt = self._by_format.get(self._fmt_jwt)
                svc = self._prefer_named(byfmt or [], ("TlsBoundJWTTokenService",))
                if svc:
                    return svc
            if "jkt" in cnf:  # DPoP binding
                byfmt = self._by_format.get(self._fmt_jwt)
                svc = self._prefer_named(byfmt or [], ("DPoPBoundJWTTokenService",))
                if svc:
                    return svc

        # 3) SSH-ish alg → SSH-CERT service
        if alg.lower().startswith("ssh-"):
            byfmt = self._by_format.get(self._fmt_ssh)
            if byfmt:
                return byfmt[0]

        # 4) Fallback by 'alg' among JWT services
        byalg = self._by_alg.get(alg.upper())
        if byalg:
            svc = self._prefer_named(byalg, ("JWTTokenService",))
            if svc:
                return svc
            return byalg[0]

        # 5) Final fallback: first registered service
        return self._services[0]

    @staticmethod
    def _prefer_named(
        services: List[ITokenService], names: Tuple[str, ...]
    ) -> Optional[ITokenService]:
        for n in names:
            for s in services:
                if getattr(s, "type", None) == n:
                    return s
        return None

    # ---------- verify ----------
    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | List[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        svc = self._select_service_for_verify(token)
        try:
            return await svc.verify(
                token, issuer=issuer, audience=audience, leeway_s=leeway_s
            )
        except Exception:
            for alt in self._services:
                if alt is svc:
                    continue
                try:
                    return await alt.verify(
                        token, issuer=issuer, audience=audience, leeway_s=leeway_s
                    )
                except Exception:
                    continue
            raise

    def _select_service_for_verify(self, token: str) -> ITokenService:
        t0 = token.strip()
        if t0.startswith("ssh-") and "-cert-" in t0.split()[0]:
            byfmt = self._by_format.get(self._fmt_ssh)
            if byfmt:
                return byfmt[0]

        if token.count(".") == 2:
            hdr, body = _peek_jwt_parts(token)
            cnf = (body or {}).get("cnf") if isinstance(body, dict) else None
            if isinstance(cnf, dict):
                if "x5t#S256" in cnf:
                    byfmt = self._by_format.get(self._fmt_jwt)
                    svc = self._prefer_named(byfmt or [], ("TlsBoundJWTTokenService",))
                    if svc:
                        return svc
                if "jkt" in cnf:
                    byfmt = self._by_format.get(self._fmt_jwt)
                    svc = self._prefer_named(byfmt or [], ("DPoPBoundJWTTokenService",))
                    if svc:
                        return svc
            typ = (hdr or {}).get("typ")
            if isinstance(typ, str):
                byfmt = self._by_format.get(typ.upper())
                if byfmt:
                    return byfmt[0]
            byfmt = self._by_format.get(self._fmt_jwt)
            if byfmt:
                svc = self._prefer_named(byfmt, ("JWTTokenService",))
                if svc:
                    return svc
                return byfmt[0]

        return self._services[0]

    # ---------- jwks ----------
    async def jwks(self) -> dict:
        merged: Dict[str, Any] = {"keys": []}
        seen_kids: set[str] = set()
        for svc in self._services:
            try:
                ks = await svc.jwks()
            except Exception:
                continue
            for jwk in ks.get("keys", []):
                kid = str(jwk.get("kid", ""))
                if not kid or kid in seen_kids:
                    continue
                merged["keys"].append(jwk)
                seen_kids.add(kid)
        return merged
