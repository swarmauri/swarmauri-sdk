"""Helper functions for loading private keys and certificate chains."""

from __future__ import annotations

from typing import List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12


def load_pem_private_key_and_chain(
    pem_bytes: bytes,
    password: Optional[bytes],
) -> Tuple[object, List[x509.Certificate]]:
    """Load a PEM private key and return it with any provided certificate chain."""

    private_key = serialization.load_pem_private_key(pem_bytes, password=password)
    return private_key, []


def load_der_private_key_and_chain(
    der_bytes: bytes,
    password: Optional[bytes],
) -> Tuple[object, List[x509.Certificate]]:
    """Load a DER private key and associated chain if available."""

    private_key = serialization.load_der_private_key(der_bytes, password=password)
    return private_key, []


def load_pfx_key_and_chain(
    pfx_bytes: bytes,
    password: Optional[bytes],
) -> Tuple[object, List[x509.Certificate]]:
    """Load a PKCS#12 archive returning the key and certificate chain."""

    private_key, cert, extra = pkcs12.load_key_and_certificates(
        pfx_bytes, password=password
    )
    chain: List[x509.Certificate] = []
    if cert is not None:
        chain.append(cert)
    if extra:
        chain.extend(extra)
    if private_key is None:
        raise ValueError("PKCS#12 archive does not contain a private key")
    return private_key, chain


__all__ = [
    "load_pem_private_key_and_chain",
    "load_der_private_key_and_chain",
    "load_pfx_key_and_chain",
]
