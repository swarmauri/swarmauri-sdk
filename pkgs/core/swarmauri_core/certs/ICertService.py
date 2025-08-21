# swarmauri_core/certs/ICertService.py
"""Certificate service interface definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Optional, Sequence, TypedDict, Dict, Any

# Reuse your canonical key reference model
from swarmauri_core.crypto.types import (
    KeyRef,
)  # kid, version, material/public, export_policy, uses, tags

# ──────────────────────────────────────────────────────────────────────────────
# Lightweight specs (intentionally library-agnostic; providers may accept more
# via the 'extensions' / 'opts' dictionaries).
# Times are UNIX epoch seconds (UTC). PEM/DER I/O is byte-oriented: providers
# should accept PEM or DER and return PEM by default (unless 'output_der=True').
# ──────────────────────────────────────────────────────────────────────────────


class SubjectSpec(TypedDict, total=False):
    CN: str
    C: str
    ST: str
    L: str
    O: str  # noqa: E741 - field name follows X.509 convention
    OU: str
    emailAddress: str
    # You can pass additional RDNs via 'extra_rdns' using provider-specific names:
    extra_rdns: Dict[str, str]


class AltNameSpec(TypedDict, total=False):
    dns: Sequence[str]  # DNS names (SAN)
    ip: Sequence[str]  # IPv4/IPv6 strings
    uri: Sequence[str]  # URI SANs
    email: Sequence[str]  # rfc822Name
    upn: Sequence[str]  # userPrincipalName (if provider supports)


class BasicConstraintsSpec(TypedDict, total=False):
    ca: bool
    path_len: Optional[int]  # None ⇒ no limit encoded


class KeyUsageSpec(TypedDict, total=False):
    digital_signature: bool
    content_commitment: bool  # nonRepudiation
    key_encipherment: bool
    data_encipherment: bool
    key_agreement: bool
    key_cert_sign: bool
    crl_sign: bool
    encipher_only: bool
    decipher_only: bool


class ExtendedKeyUsageSpec(TypedDict, total=False):
    # Either OID strings (e.g., "1.3.6.1.5.5.7.3.1") or common tokens ("serverAuth", "clientAuth", ...)
    oids: Sequence[str]


class NameConstraintsSpec(TypedDict, total=False):
    permitted_dns: Sequence[str]
    excluded_dns: Sequence[str]
    permitted_ip: Sequence[str]
    excluded_ip: Sequence[str]
    permitted_uri: Sequence[str]
    excluded_uri: Sequence[str]
    permitted_email: Sequence[str]
    excluded_email: Sequence[str]


class CertExtensionSpec(TypedDict, total=False):
    basic_constraints: BasicConstraintsSpec
    key_usage: KeyUsageSpec
    extended_key_usage: ExtendedKeyUsageSpec
    name_constraints: NameConstraintsSpec
    subject_alt_name: AltNameSpec  # convenience; same as 'san' input
    subject_key_identifier: bool  # auto‑derive from subject public key
    authority_key_identifier: (
        bool  # auto‑derive from issuer (requires ca_cert or ca public)
    )
    # Provider-specific or advanced extensions may be passed in 'extra':
    extra: Dict[str, Any]


# Common alias for PEM/DER bytes
CertBytes = bytes
CsrBytes = bytes


class ICertService(ABC):
    """
    X.509 / CSR service surface.

    Responsibilities
    ----------------
    - Build and sign PKCS#10 CSRs from a KeyRef.
    - Issue X.509 certificates (self-signed or from CSR) with standard extensions.
    - Verify X.509 certificates against trust roots / intermediates.
    - Parse certificate/CSR metadata for API responses / audits.

    Conventions
    -----------
    - All methods are async to align with your async-first design.
    - Inputs/outputs are bytes (PEM preferred on output). A provider MAY accept
      both PEM and DER; it SHOULD return PEM unless 'output_der=True' is set.
    - 'sig_alg' should be a stable token understood by the provider, e.g.:
        "Ed25519", "RSA-PSS-SHA256", "ECDSA-P256-SHA256"
      If omitted, providers MAY choose a sensible default based on the key.
    """

    # ───────────────────────────── capability probe ─────────────────────────────

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """
        Report advertised capabilities, e.g.:
        {
          "key_algs":   ("Ed25519","RSA-2048","RSA-3072","EC-P256"),
          "sig_algs":   ("Ed25519","RSA-PSS-SHA256","ECDSA-P256-SHA256"),
          "features":   ("csr","self_signed","sign_from_csr","verify","parse","san","eku","key_usage","akid","skid"),
          "profiles":   ("server","client","code_signing")  # optional tokens for opinionated presets
        }
        """
        ...

    # ─────────────────────────────── CSR (PKCS#10) ──────────────────────────────

    @abstractmethod
    async def create_csr(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        san: Optional[AltNameSpec] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        challenge_password: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CsrBytes:
        """
        Build and sign a PKCS#10 CSR using 'key' (private key in KeyRef.material or HSM handle).

        Returns:
            CSR in PEM (default) or DER if output_der=True.

        Notes:
        - 'extensions' here are *requested* extensions; final issuance may override.
        - Implementations SHOULD include the public key from 'key' in the CSR.
        - If the underlying key is non‑exportable, providers MUST still sign via handle.
        """
        ...

    # ─────────────────────── Certificates (self-signed / CA) ────────────────────

    @abstractmethod
    async def create_self_signed(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        """
        Create a self-signed certificate using 'key' as both subject and issuer.

        Providers SHOULD:
        - Default not_before to now‑300s and not_after to now+365d if not provided.
        - Emit SKID; omit AKID (issuer=self).
        - Respect 'extensions' (e.g., basic_constraints.ca=false for leafs).
        """
        ...

    @abstractmethod
    async def sign_cert(
        self,
        csr: CsrBytes,
        ca_key: KeyRef,
        *,
        issuer: Optional[
            SubjectSpec
        ] = None,  # override CSR subject as issuer DN (if omitted, derive from ca_cert when available)
        ca_cert: Optional[
            CertBytes
        ] = None,  # used for AKID, issuer DN, and chain building
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        """
        Issue an end‑entity or intermediate certificate from a CSR using 'ca_key'.

        Behavior:
        - If 'ca_cert' provided, use its subject as issuer DN and derive AKID from it.
        - If 'extensions.basic_constraints.ca' is True, you are minting an intermediate.
        - Providers SHOULD validate CSR signature and subject public key before signing.
        """
        ...

    # ───────────────────────────────── verification ─────────────────────────────

    @abstractmethod
    async def verify_cert(
        self,
        cert: CertBytes,
        *,
        trust_roots: Optional[Sequence[CertBytes]] = None,
        intermediates: Optional[Sequence[CertBytes]] = None,
        check_time: Optional[int] = None,  # epoch seconds; default = now
        check_revocation: bool = False,  # provider MAY NOT implement revocation; if unsupported, ignore
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Verify an X.509 certificate and (optionally) its chain.

        Returns a structured result, e.g.:
          {
            "valid": True,
            "reason": None,
            "issuer": "...", "subject": "...",
            "not_before": 1710000000, "not_after": 1740000000,
            "chain_len": 2, "is_ca": False,
          }

        Notes:
        - If 'trust_roots' is None, providers MAY verify only signature and validity window.
        - Revocation checking is provider‑specific; unsupported providers should set {"revocation_checked": False}.
        """
        ...

    # ────────────────────────────────── parsing ─────────────────────────────────

    @abstractmethod
    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Parse an X.509 certificate into a JSON‑serializable mapping suitable for APIs/UX.

        Suggested shape:
          {
            "tbs_version": 3,
            "serial": 123456789,
            "sig_alg": "RSA-PSS-SHA256",
            "issuer": {"C":"US","O":"Acme","CN":"Acme Root CA"},
            "subject": {"C":"US","O":"Acme","CN":"service.acme.test"},
            "not_before": 1710000000,
            "not_after": 1740000000,
            "skid": "ab:cd:..",
            "akid": "ef:01:..",
            "san": {"dns": ["service.acme.test","api.acme.test"]},
            "eku": ["serverAuth","clientAuth"],     # or OIDs
            "key_usage": {...},
            "is_ca": False,
          }
        """
        ...
