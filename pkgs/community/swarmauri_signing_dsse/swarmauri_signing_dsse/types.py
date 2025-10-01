"""Typed representations of DSSE envelope structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class DSSESignatureRecord:
    """Represent a DSSE signature record in the JSON envelope."""

    sig: str
    keyid: Optional[str] = None
    cert: Optional[str] = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "DSSESignatureRecord":
        """Construct a signature record from a mapping."""

        if "sig" not in data:
            raise ValueError("DSSE signature mapping is missing the 'sig' field")
        sig_value = data["sig"]
        if not isinstance(sig_value, str):
            raise TypeError("DSSE signature field 'sig' must be a base64 string")

        keyid_value = data.get("keyid")
        if keyid_value is not None and not isinstance(keyid_value, str):
            raise TypeError(
                "DSSE signature field 'keyid' must be a string when provided"
            )

        cert_value = data.get("cert")
        if cert_value is not None and not isinstance(cert_value, str):
            raise TypeError(
                "DSSE signature field 'cert' must be a PEM string when provided"
            )

        return cls(sig=sig_value, keyid=keyid_value, cert=cert_value)

    def to_mapping(self) -> MutableMapping[str, str]:
        """Return the JSON-serializable mapping representation."""

        mapping: MutableMapping[str, str] = {"sig": self.sig}
        if self.keyid is not None:
            mapping["keyid"] = self.keyid
        if self.cert is not None:
            mapping["cert"] = self.cert
        return mapping


@dataclass(frozen=True)
class DSSEEnvelope:
    """Immutable DSSE envelope compatible with the JSON wire format."""

    payload_type: str
    payload_b64: str
    signatures: Sequence[DSSESignatureRecord] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate field types and normalize signatures."""

        if not isinstance(self.payload_type, str) or not self.payload_type:
            raise ValueError("payload_type must be a non-empty string")
        if not isinstance(self.payload_b64, str):
            raise TypeError("payload_b64 must be a base64-encoded string")

        normalized: Tuple[DSSESignatureRecord, ...] = tuple(
            self._coerce_signature(sig) for sig in self.signatures
        )
        object.__setattr__(self, "signatures", normalized)

    @staticmethod
    def _coerce_signature(
        signature: DSSESignatureRecord | Mapping[str, object],
    ) -> DSSESignatureRecord:
        """Normalize signature inputs to :class:`DSSESignatureRecord`."""

        if isinstance(signature, DSSESignatureRecord):
            return signature
        if isinstance(signature, Mapping):
            return DSSESignatureRecord.from_mapping(signature)
        raise TypeError("Unsupported signature representation in DSSE envelope")

    def to_mapping(self) -> MutableMapping[str, object]:
        """Return the JSON-serializable mapping representation of the envelope."""

        return {
            "payloadType": self.payload_type,
            "payload": self.payload_b64,
            "signatures": [sig.to_mapping() for sig in self.signatures],
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "DSSEEnvelope":
        """Build a DSSE envelope from a decoded JSON mapping."""

        if "payloadType" not in data:
            raise ValueError("DSSE envelope mapping missing 'payloadType'")
        if "payload" not in data:
            raise ValueError("DSSE envelope mapping missing 'payload'")

        payload_type = data["payloadType"]
        payload_b64 = data["payload"]
        signatures: Iterable[Mapping[str, object]] = data.get("signatures", [])  # type: ignore[assignment]

        if not isinstance(payload_type, str) or not payload_type:
            raise ValueError("payloadType must be a non-empty string")
        if not isinstance(payload_b64, str):
            raise TypeError("payload must be a base64 string")

        if not isinstance(signatures, Iterable):
            raise TypeError("signatures must be an iterable of mappings")

        normalized_signatures = [cls._coerce_signature(sig) for sig in signatures]
        return cls(
            payload_type=payload_type,
            payload_b64=payload_b64,
            signatures=normalized_signatures,
        )

    def without_signatures(self) -> "DSSEEnvelope":
        """Return a copy of the envelope without signature records."""

        return DSSEEnvelope(
            payload_type=self.payload_type, payload_b64=self.payload_b64, signatures=()
        )
