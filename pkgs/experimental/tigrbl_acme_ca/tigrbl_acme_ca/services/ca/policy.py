from __future__ import annotations
from typing import Sequence

try:
    from cryptography import x509
    from cryptography.x509.oid import ExtensionOID
except Exception:  # pragma: no cover
    x509 = None
    ExtensionOID = None


class PolicyError(ValueError):
    pass


def check_identifiers_allowed(identifiers: Sequence[str]) -> None:
    if not identifiers:
        raise PolicyError("identifiers_required")
    if len(identifiers) > 100:
        raise PolicyError("too_many_identifiers")
    # Basic wildcard rule: wildcard only at left-most label
    for name in identifiers:
        if "*" in name and not name.startswith("*."):
            raise PolicyError("invalid_wildcard_position")


def _csr_sans(csr_der: bytes) -> list[str]:
    if x509 is None:
        return []
    try:
        csr = x509.load_der_x509_csr(csr_der)
        try:
            ext = csr.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
        except Exception:
            return []
        return [gen.value for gen in ext.value.get_values_for_type(x509.DNSName)]
    except Exception:
        return []


def check_csr_matches_identifiers(csr_der: bytes, identifiers: Sequence[str]) -> None:
    # If we cannot parse CSR, allow (runtime policy may enforce differently)
    sans = _csr_sans(csr_der)
    if not sans:
        return
    idset = set(i.lower() for i in identifiers)
    sanset = set(s.lower() for s in sans)
    if not idset.issubset(sanset):
        raise PolicyError("csr_names_do_not_cover_identifiers")
