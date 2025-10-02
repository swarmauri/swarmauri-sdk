from __future__ import annotations

import datetime
import ipaddress
import time
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from acme import client, errors, messages
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.x509.oid import (
    AttributeOID,
    ExtendedKeyUsageOID,
    NameOID,
    ObjectIdentifier,
)
from josepy import jwk

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef

ACME_DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"


_UPN_OID = ObjectIdentifier("1.3.6.1.4.1.311.20.2.3")
_EKU_ALIASES: Dict[str, ObjectIdentifier] = {
    "serverAuth": ExtendedKeyUsageOID.SERVER_AUTH,
    "clientAuth": ExtendedKeyUsageOID.CLIENT_AUTH,
    "codeSigning": ExtendedKeyUsageOID.CODE_SIGNING,
    "emailProtection": ExtendedKeyUsageOID.EMAIL_PROTECTION,
    "timeStamping": ExtendedKeyUsageOID.TIME_STAMPING,
    "ocspSigning": ExtendedKeyUsageOID.OCSP_SIGNING,
}


def _ts(value: datetime.datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    return int(value.timestamp())


def _build_name(subject: SubjectSpec) -> x509.Name:
    if not subject:
        raise ValueError("subject must include at least one attribute")

    rdns = []
    mapping: Tuple[Tuple[str, NameOID], ...] = (
        ("C", NameOID.COUNTRY_NAME),
        ("ST", NameOID.STATE_OR_PROVINCE_NAME),
        ("L", NameOID.LOCALITY_NAME),
        ("O", NameOID.ORGANIZATION_NAME),
        ("OU", NameOID.ORGANIZATIONAL_UNIT_NAME),
        ("CN", NameOID.COMMON_NAME),
        ("emailAddress", NameOID.EMAIL_ADDRESS),
    )

    for key, oid in mapping:
        value = subject.get(key)
        if value:
            rdns.append(x509.NameAttribute(oid, value))

    for raw_oid, value in subject.get("extra_rdns", {}).items():
        if not value:
            continue
        try:
            oid = ObjectIdentifier(raw_oid)
        except Exception:
            try:
                oid = getattr(NameOID, raw_oid)
            except AttributeError:
                oid = ObjectIdentifier(raw_oid)
        rdns.append(x509.NameAttribute(oid, value))

    if not rdns:
        raise ValueError("subject must include at least one attribute")
    return x509.Name(rdns)


def _build_san(san: Optional[AltNameSpec]) -> Optional[x509.SubjectAlternativeName]:
    if not san:
        return None

    entries: List[x509.GeneralName] = []
    for dns in san.get("dns", []) or []:
        entries.append(x509.DNSName(dns))
    for email in san.get("email", []) or []:
        entries.append(x509.RFC822Name(email))
    for uri in san.get("uri", []) or []:
        entries.append(x509.UniformResourceIdentifier(uri))
    for ip in san.get("ip", []) or []:
        entries.append(x509.IPAddress(ipaddress.ip_address(ip)))
    for upn in san.get("upn", []) or []:
        entries.append(x509.OtherName(_UPN_OID, upn.encode("utf-16-le")))

    return x509.SubjectAlternativeName(entries) if entries else None


def _merge_san(
    first: Optional[x509.SubjectAlternativeName],
    second: Optional[x509.SubjectAlternativeName],
) -> Optional[x509.SubjectAlternativeName]:
    if first is None:
        return second
    if second is None:
        return first
    combined = list(first)
    combined.extend(second)
    # Remove duplicates while preserving order
    unique: List[x509.GeneralName] = []
    seen = set()
    for item in combined:
        key = (type(item), getattr(item, "value", None))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return x509.SubjectAlternativeName(unique)


def _load_private_key(material: bytes):
    try:
        return serialization.load_pem_private_key(material, password=None)
    except ValueError:
        return serialization.load_der_private_key(material, password=None)


def _select_sig_hash(
    priv_key, sig_alg: Optional[str]
) -> Optional[hashes.HashAlgorithm]:
    token = (sig_alg or "").upper()
    if token in {"RS384", "RSA-SHA384"}:
        return hashes.SHA384()
    if token in {"RS512", "RSA-SHA512"}:
        return hashes.SHA512()
    if token in {"RS256", "RSA", "RSA-SHA256"}:
        return hashes.SHA256()
    if token in {"ES384", "ECDSA-P384", "ECDSA-SHA384"}:
        return hashes.SHA384()
    if token in {"ES512", "ECDSA-P521", "ECDSA-SHA512"}:
        return hashes.SHA512()
    if token in {"ES256", "ECDSA", "ECDSA-P256", "ECDSA-SHA256"}:
        return hashes.SHA256()

    if isinstance(priv_key, rsa.RSAPrivateKey):
        return hashes.SHA256()
    if isinstance(priv_key, ec.EllipticCurvePrivateKey):
        curve = priv_key.curve
        if isinstance(curve, ec.SECP384R1):
            return hashes.SHA384()
        if isinstance(curve, ec.SECP521R1):
            return hashes.SHA512()
        return hashes.SHA256()
    if isinstance(priv_key, ed25519.Ed25519PrivateKey):
        return None

    raise ValueError("Unsupported key type for signing")


def _add_extension_requests(
    builder: x509.CertificateSigningRequestBuilder,
    san: Optional[AltNameSpec],
    extensions: Optional[CertExtensionSpec],
    public_key: Any,
) -> x509.CertificateSigningRequestBuilder:
    ext_spec = extensions or {}

    san_ext = _merge_san(_build_san(san), _build_san(ext_spec.get("subject_alt_name")))
    if san_ext:
        builder = builder.add_extension(san_ext, critical=False)

    if "basic_constraints" in ext_spec:
        bc = ext_spec["basic_constraints"]
        builder = builder.add_extension(
            x509.BasicConstraints(
                ca=bool(bc.get("ca", False)),
                path_length=bc.get("path_len"),
            ),
            critical=True,
        )

    if "key_usage" in ext_spec:
        ku = ext_spec["key_usage"]
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=bool(ku.get("digital_signature", False)),
                content_commitment=bool(ku.get("content_commitment", False)),
                key_encipherment=bool(ku.get("key_encipherment", False)),
                data_encipherment=bool(ku.get("data_encipherment", False)),
                key_agreement=bool(ku.get("key_agreement", False)),
                key_cert_sign=bool(ku.get("key_cert_sign", False)),
                crl_sign=bool(ku.get("crl_sign", False)),
                encipher_only=bool(ku.get("encipher_only", False)),
                decipher_only=bool(ku.get("decipher_only", False)),
            ),
            critical=True,
        )

    if "extended_key_usage" in ext_spec:
        eku_spec = ext_spec["extended_key_usage"].get("oids", []) or []
        eku_oids = []
        for token in eku_spec:
            if not token:
                continue
            if token in _EKU_ALIASES:
                eku_oids.append(_EKU_ALIASES[token])
            else:
                eku_oids.append(ObjectIdentifier(token))
        if eku_oids:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage(eku_oids),
                critical=False,
            )

    if "name_constraints" in ext_spec:
        nc = ext_spec["name_constraints"]

        def _dns(seq: Optional[Sequence[str]]) -> List[x509.GeneralName]:
            return [x509.DNSName(v) for v in (seq or [])]

        def _uri(seq: Optional[Sequence[str]]) -> List[x509.GeneralName]:
            return [x509.UniformResourceIdentifier(v) for v in (seq or [])]

        def _ip(seq: Optional[Sequence[str]]) -> List[x509.GeneralName]:
            return [
                x509.IPAddress(ipaddress.ip_network(v, strict=False))
                for v in (seq or [])
            ]

        def _email(seq: Optional[Sequence[str]]) -> List[x509.GeneralName]:
            return [x509.RFC822Name(v) for v in (seq or [])]

        permitted = _dns(nc.get("permitted_dns"))
        permitted += _uri(nc.get("permitted_uri"))
        permitted += _ip(nc.get("permitted_ip"))
        permitted += _email(nc.get("permitted_email"))

        excluded = _dns(nc.get("excluded_dns"))
        excluded += _uri(nc.get("excluded_uri"))
        excluded += _ip(nc.get("excluded_ip"))
        excluded += _email(nc.get("excluded_email"))

        builder = builder.add_extension(
            x509.NameConstraints(
                permitted_subtrees=permitted or None,
                excluded_subtrees=excluded or None,
            ),
            critical=True,
        )

    if ext_spec.get("subject_key_identifier"):
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(public_key),
            critical=False,
        )

    extra = ext_spec.get("extra") or {}
    for oid_text, payload in extra.items():
        if payload is None:
            continue
        critical = False
        value: bytes
        if isinstance(payload, dict):
            critical = bool(payload.get("critical", False))
            value = payload.get("value", b"")
        elif isinstance(payload, (bytes, bytearray)):
            value = bytes(payload)
        else:
            value = str(payload).encode("utf-8")
        builder = builder.add_extension(
            x509.UnrecognizedExtension(ObjectIdentifier(oid_text), value),
            critical=critical,
        )

    return builder


def _pem_chain_to_certs(data: bytes) -> List[x509.Certificate]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [x509.load_der_x509_certificate(data)]

    certs: List[x509.Certificate] = []
    marker = "-----BEGIN CERTIFICATE-----"
    end_marker = "-----END CERTIFICATE-----"
    start = 0
    while True:
        begin = text.find(marker, start)
        if begin == -1:
            break
        finish = text.find(end_marker, begin)
        if finish == -1:
            break
        finish += len(end_marker)
        chunk = text[begin:finish]
        certs.append(x509.load_pem_x509_certificate(chunk.encode("utf-8")))
        start = finish

    if not certs:
        raise ValueError("No certificates found in input")
    return certs


def _load_cert_any(data: bytes) -> x509.Certificate:
    try:
        return x509.load_pem_x509_certificate(data)
    except ValueError:
        return x509.load_der_x509_certificate(data)


def _name_to_str(name: x509.Name) -> str:
    return ", ".join(f"{attr.oid.dotted_string}={attr.value}" for attr in name)


def _name_to_mapping(name: x509.Name) -> Dict[str, str]:
    out: Dict[str, str] = {}
    mapping = {
        NameOID.COUNTRY_NAME: "C",
        NameOID.STATE_OR_PROVINCE_NAME: "ST",
        NameOID.LOCALITY_NAME: "L",
        NameOID.ORGANIZATION_NAME: "O",
        NameOID.ORGANIZATIONAL_UNIT_NAME: "OU",
        NameOID.COMMON_NAME: "CN",
        NameOID.EMAIL_ADDRESS: "emailAddress",
    }
    for attribute in name:
        key = mapping.get(attribute.oid, attribute.oid.dotted_string)
        out[key] = attribute.value
    return out


def _is_ca(cert: x509.Certificate) -> bool:
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        return bool(bc.ca)
    except x509.ExtensionNotFound:
        return False


def _verify_signed_by(child: x509.Certificate, issuer: x509.Certificate) -> None:
    public_key = issuer.public_key()
    if isinstance(public_key, rsa.RSAPublicKey):
        public_key.verify(
            child.signature,
            child.tbs_certificate_bytes,
            asym_padding.PKCS1v15(),
            child.signature_hash_algorithm,
        )
        return
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        public_key.verify(
            child.signature,
            child.tbs_certificate_bytes,
            ec.ECDSA(child.signature_hash_algorithm),
        )
        return
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        public_key.verify(child.signature, child.tbs_certificate_bytes)
        return
    raise ValueError("Unsupported issuer key type")


def _verify_self_signed(cert: x509.Certificate) -> None:
    _verify_signed_by(cert, cert)


class AcmeCertService(CertServiceBase):
    """ACME v2 certificate service implementing RFC 8555.

    This service handles PKCS#10 CSRs (RFC 2986) and returns X.509
    certificates (RFC 5280).
    """

    type: Literal["AcmeCertService"] = "AcmeCertService"

    def __init__(
        self,
        account_key: KeyRef,
        *,
        directory_url: str = ACME_DIRECTORY_URL,
        contact_emails: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__()
        self._account_key = account_key
        self._dir_url = directory_url
        self._contact = contact_emails or []

        self._client: Optional[client.ClientV2] = None

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "RSA-4096", "EC-P256", "EC-P384"),
            "sig_algs": ("RS256", "RS384", "RS512", "ES256", "ES384", "ES512"),
            "features": (
                "acme",
                "csr",
                "sign_from_csr",
                "verify",
                "parse",
                "san",
                "chain",
            ),
            "profiles": ("server", "client"),
        }

    def _ensure_client(self) -> client.ClientV2:
        if self._client:
            return self._client

        if self._account_key.material is None:
            raise RuntimeError("Account key material is required for ACME")
        key = jwk.JWK.load(self._account_key.material)
        net = client.ClientNetwork(key, user_agent="swarmauri-acme/1.0")
        directory = messages.Directory.from_json(net.get(self._dir_url).json())
        cl = client.ClientV2(directory, net=net)

        contacts = [f"mailto:{email}" for email in self._contact if email]
        registration_kwargs: Dict[str, Any] = {"terms_of_service_agreed": True}
        if contacts:
            registration_kwargs["contact"] = tuple(contacts)
        new_account = messages.NewRegistration.from_data(**registration_kwargs)
        try:
            cl.new_account(new_account)
        except errors.ConflictError as conflict:
            cl.query_registration(messages.RegistrationResource(uri=conflict.location))

        self._client = cl
        return cl

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
        if not key.material:
            raise RuntimeError("Private key material required to build CSR")

        private_key = _load_private_key(key.material)
        builder = x509.CertificateSigningRequestBuilder().subject_name(
            _build_name(subject)
        )

        builder = _add_extension_requests(
            builder,
            san,
            extensions,
            private_key.public_key(),
        )

        if challenge_password:
            builder = builder.add_attribute(
                AttributeOID.CHALLENGE_PASSWORD,
                challenge_password.encode("utf-8"),
            )

        signature_alg = _select_sig_hash(private_key, sig_alg)
        csr = builder.sign(private_key, signature_alg)
        encoding = (
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return csr.public_bytes(encoding)

    async def sign_cert(
        self,
        csr: CsrBytes,
        ca_key: KeyRef,
        *,
        issuer: Optional[SubjectSpec] = None,
        ca_cert: Optional[CertBytes] = None,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        opts = opts or {}
        client_v2 = self._ensure_client()

        try:
            x509.load_pem_x509_csr(csr)
            csr_bytes = csr
        except ValueError:
            csr_obj = x509.load_der_x509_csr(csr)
            csr_bytes = csr_obj.public_bytes(serialization.Encoding.PEM)

        profile = opts.get("profile") or opts.get("order_profile")
        order = client_v2.new_order(csr_bytes, profile=profile)

        deadline = None
        if "finalize_deadline" in opts:
            deadline_val = opts["finalize_deadline"]
            if isinstance(deadline_val, datetime.datetime):
                deadline = deadline_val
            else:
                deadline = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=float(deadline_val))
        elif "finalize_timeout" in opts:
            deadline = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=float(opts["finalize_timeout"]))

        finalized = client_v2.poll_and_finalize(order, deadline=deadline)

        candidates = [finalized.fullchain_pem]
        candidates.extend(finalized.alternative_fullchains_pem or [])
        chain_choice = opts.get("prefer_chain")
        chosen_chain = candidates[0]
        if chain_choice is not None:
            if isinstance(chain_choice, int) and 0 <= chain_choice < len(candidates):
                chosen_chain = candidates[chain_choice]
            elif isinstance(chain_choice, str):
                chosen_chain = next(
                    (chain for chain in candidates if chain_choice in chain),
                    candidates[0],
                )

        pem_bytes = chosen_chain.encode("utf-8")
        if not output_der:
            return pem_bytes

        certs = _pem_chain_to_certs(pem_bytes)
        return b"".join(c.public_bytes(serialization.Encoding.DER) for c in certs)

    async def create_self_signed(self, *a, **kw) -> CertBytes:  # pragma: no cover
        raise NotImplementedError("Self-signed not supported in AcmeCertService")

    async def verify_cert(
        self,
        cert: CertBytes,
        *,
        trust_roots: Optional[Sequence[CertBytes]] = None,
        intermediates: Optional[Sequence[CertBytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        del opts  # unused placeholder for future expansion

        chain = _pem_chain_to_certs(cert)
        leaf = chain[0]

        now = int(check_time) if check_time is not None else int(time.time())
        if now < _ts(leaf.not_valid_before):
            return {"valid": False, "reason": "not_yet_valid"}
        if now > _ts(leaf.not_valid_after):
            return {"valid": False, "reason": "expired"}

        intermediates_pool: Dict[str, x509.Certificate] = {
            _name_to_str(c.subject): c for c in chain[1:]
        }
        for extra in intermediates or []:
            for parsed in _pem_chain_to_certs(extra):
                intermediates_pool.setdefault(_name_to_str(parsed.subject), parsed)

        root_certs = [
            cert_obj
            for bundle in (trust_roots or [])
            for cert_obj in _pem_chain_to_certs(bundle)
        ]

        current = leaf
        chain_len = 1
        while True:
            issuer_dn = _name_to_str(current.issuer)
            subject_dn = _name_to_str(current.subject)

            root_candidate = next(
                (
                    root
                    for root in root_certs
                    if _name_to_str(root.subject) == issuer_dn
                ),
                None,
            )
            if root_candidate is not None:
                _verify_signed_by(current, root_candidate)
                _verify_self_signed(root_candidate)
                if subject_dn != issuer_dn:
                    chain_len += 1
                return {
                    "valid": True,
                    "reason": None,
                    "chain_len": chain_len,
                    "issuer": _name_to_str(leaf.issuer),
                    "subject": _name_to_str(leaf.subject),
                    "not_before": _ts(leaf.not_valid_before),
                    "not_after": _ts(leaf.not_valid_after),
                    "revocation_checked": False if check_revocation else False,
                }

            if subject_dn == issuer_dn and not trust_roots:
                _verify_self_signed(current)
                return {
                    "valid": True,
                    "reason": None,
                    "chain_len": chain_len,
                    "issuer": _name_to_str(leaf.issuer),
                    "subject": _name_to_str(leaf.subject),
                    "not_before": _ts(leaf.not_valid_before),
                    "not_after": _ts(leaf.not_valid_after),
                    "revocation_checked": False if check_revocation else False,
                }

            next_cert = intermediates_pool.pop(issuer_dn, None)
            if next_cert is None:
                reason = (
                    "incomplete_chain" if trust_roots else "untrusted_without_roots"
                )
                return {"valid": False, "reason": reason}

            _verify_signed_by(current, next_cert)
            current = next_cert
            chain_len += 1

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        del opts  # reserved for future options

        certificate = _pem_chain_to_certs(cert)[0]
        info: Dict[str, Any] = {
            "serial": int(certificate.serial_number),
            "sig_alg": (
                certificate.signature_hash_algorithm.name
                if certificate.signature_hash_algorithm
                else "unknown"
            ),
            "issuer": _name_to_mapping(certificate.issuer),
            "subject": _name_to_mapping(certificate.subject),
            "not_before": _ts(certificate.not_valid_before),
            "not_after": _ts(certificate.not_valid_after),
            "is_ca": _is_ca(certificate),
        }

        if include_extensions:
            try:
                skid = certificate.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value.digest
                info["skid"] = skid.hex(":")
            except x509.ExtensionNotFound:
                pass

            try:
                akid = certificate.extensions.get_extension_for_class(
                    x509.AuthorityKeyIdentifier
                ).value.key_identifier
                if akid:
                    info["akid"] = akid.hex(":")
            except x509.ExtensionNotFound:
                pass

            try:
                san = certificate.extensions.get_extension_for_class(
                    x509.SubjectAlternativeName
                ).value
                info["san"] = {
                    "dns": [
                        value.value for value in san.get_values_for_type(x509.DNSName)
                    ],
                    "ip": [
                        str(value) for value in san.get_values_for_type(x509.IPAddress)
                    ],
                    "uri": [
                        value.value
                        for value in san.get_values_for_type(
                            x509.UniformResourceIdentifier
                        )
                    ],
                    "email": [
                        value.value
                        for value in san.get_values_for_type(x509.RFC822Name)
                    ],
                }
            except x509.ExtensionNotFound:
                pass

            try:
                eku = certificate.extensions.get_extension_for_class(
                    x509.ExtendedKeyUsage
                ).value
                info["eku"] = [oid.dotted_string for oid in eku]
            except x509.ExtensionNotFound:
                pass

            try:
                ku = certificate.extensions.get_extension_for_class(x509.KeyUsage).value
                info["key_usage"] = {
                    "digital_signature": ku.digital_signature,
                    "content_commitment": ku.content_commitment,
                    "key_encipherment": ku.key_encipherment,
                    "data_encipherment": ku.data_encipherment,
                    "key_agreement": ku.key_agreement,
                    "key_cert_sign": ku.key_cert_sign,
                    "crl_sign": ku.crl_sign,
                    "encipher_only": ku.encipher_only,
                    "decipher_only": ku.decipher_only,
                }
            except x509.ExtensionNotFound:
                pass

        return info
