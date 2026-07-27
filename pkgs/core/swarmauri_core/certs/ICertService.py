from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Sequence, TypedDict

from swarmauri_core.crypto.types import (
    KeyRef,
)  # kid, version, material/public, export_policy, uses, tags

# -----------------------------------------------------------------------------
# Lightweight specs (intentionally library-agnostic; providers may accept more
# via the 'extensions' / 'opts' dictionaries).
# Times are UNIX epoch seconds (UTC). PEM/DER I/O is byte-oriented: providers
# should accept PEM or DER and return PEM by default (unless
# 'output_der=True').
# -----------------------------------------------------------------------------


class SubjectSpec(TypedDict, total=False):
    CN: str
    C: str
    ST: str
    L: str
    O: str  # noqa: E741 - X.509 standard abbreviation for organization
    OU: str
    emailAddress: str
    # You can pass additional RDNs via 'extra_rdns' using provider-specific
    # names:
    extra_rdns: dict[str, str]


class AltNameSpec(TypedDict, total=False):
    dns: Sequence[str]  # DNS names (SAN)
    ip: Sequence[str]  # IPv4/IPv6 strings
    uri: Sequence[str]  # URI SANs
    email: Sequence[str]  # rfc822Name
    upn: Sequence[str]  # userPrincipalName (if provider supports)


class BasicConstraintsSpec(TypedDict, total=False):
    ca: bool
    path_len: int | None  # None ⇒ no limit encoded


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
    # Either OID strings (e.g., "1.3.6.1.5.5.7.3.1") or common tokens
    # ("serverAuth", "clientAuth", ...)
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
    subject_key_identifier: bool  # auto-derive from subject public key
    authority_key_identifier: (
        bool  # auto-derive from issuer (requires ca_cert or ca public)
    )
    # Provider-specific or advanced extensions may be passed in 'extra':
    extra: dict[str, Any]


# Common alias for PEM/DER bytes
CertBytes = bytes
CsrBytes = bytes


class ICertService(ABC):
    """X.509 / CSR service surface following RFC 5280 and RFC 2986."""

    # ------------------------------------------------------------------
    # capability probe
    # ------------------------------------------------------------------

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Report advertised capabilities."""
        ...

    # ------------------------------------------------------------------
    # CSR (PKCS#10 - RFC 2986)
    # ------------------------------------------------------------------

    @abstractmethod
    async def create_csr(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        san: AltNameSpec | None = None,
        extensions: CertExtensionSpec | None = None,
        sig_alg: str | None = None,
        challenge_password: str | None = None,
        output_der: bool = False,
        opts: dict[str, Any] | None = None,
    ) -> CsrBytes:
        """Build and sign a PKCS#10 CSR (RFC 2986) using 'key'."""
        ...

    # ------------------------------------------------------------------
    # Certificates (self-signed / CA) - RFC 5280
    # ------------------------------------------------------------------

    @abstractmethod
    async def create_self_signed(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        serial: int | None = None,
        not_before: int | None = None,
        not_after: int | None = None,
        extensions: CertExtensionSpec | None = None,
        sig_alg: str | None = None,
        output_der: bool = False,
        opts: dict[str, Any] | None = None,
    ) -> CertBytes:
        """Create a self-signed certificate using 'key' as both subject and
        issuer."""
        ...

    @abstractmethod
    async def sign_cert(
        self,
        csr: CsrBytes,
        ca_key: KeyRef,
        *,
        issuer: SubjectSpec | None = None,
        ca_cert: CertBytes | None = None,
        serial: int | None = None,
        not_before: int | None = None,
        not_after: int | None = None,
        extensions: CertExtensionSpec | None = None,
        sig_alg: str | None = None,
        output_der: bool = False,
        opts: dict[str, Any] | None = None,
    ) -> CertBytes:
        """Issue an end-entity or intermediate certificate from a CSR."""
        ...

    # ------------------------------------------------------------------
    # verification
    # ------------------------------------------------------------------

    @abstractmethod
    async def verify_cert(
        self,
        cert: CertBytes,
        *,
        trust_roots: Sequence[CertBytes] | None = None,
        intermediates: Sequence[CertBytes] | None = None,
        check_time: int | None = None,
        check_revocation: bool = False,
        opts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Verify an X.509 certificate and optionally its chain."""
        ...

    # ------------------------------------------------------------------
    # parsing
    # ------------------------------------------------------------------

    @abstractmethod
    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Parse an X.509 certificate into a JSON-serializable mapping."""
        ...
