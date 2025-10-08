from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Sequence, Tuple

import base64
import binascii

import httpx

from .adapters import Txn


class WorkloadClientError(RuntimeError):
    """Raised when the custom workload client cannot satisfy a request."""


class _Certificate:
    __slots__ = ("_der",)

    def __init__(self, der: bytes) -> None:
        self._der = der

    def public_bytes(self) -> bytes:  # pragma: no cover - trivial proxy
        return self._der


@dataclass(slots=True)
class X509Svid:
    _spiffe_id: str
    _cert_chain: Tuple[_Certificate, ...]
    _expires_at: datetime

    def spiffe_id(self) -> str:
        return self._spiffe_id

    @property
    def cert_chain(self) -> Tuple[_Certificate, ...]:
        return self._cert_chain

    @property
    def expires_at(self) -> datetime:
        return self._expires_at


class UnixWorkloadClient:
    """Minimal HTTP-over-UDS workload client used in place of ``py-spiffe``.

    The client expects a SPIFFE agent to expose REST-like endpoints that mirror
    the Workload API semantics. This keeps the runtime self-contained while
    providing deterministic behaviour for tests.
    """

    def __init__(self, socket_path: str, *, timeout: float = 5.0) -> None:
        if not socket_path:
            raise WorkloadClientError("Unix socket path is required")
        transport = httpx.HTTPTransport(uds=socket_path)
        self._client = httpx.Client(transport=transport, timeout=timeout)

    def fetch_x509_svid(self, *, aud: Sequence[str] = ()) -> X509Svid:
        response = self._client.post("/workload/x509svid", json={"aud": list(aud)})
        response.raise_for_status()
        data = response.json()

        spiffe_id = data.get("spiffe_id")
        if not spiffe_id:
            raise WorkloadClientError("Missing spiffe_id in workload response")

        chain = _coerce_cert_chain(data)
        expires_at = _coerce_expires_at(data)

        return X509Svid(spiffe_id, chain, expires_at)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "UnixWorkloadClient":  # pragma: no cover - context protocol
        return self

    def __exit__(
        self, exc_type, exc, tb
    ) -> None:  # pragma: no cover - context protocol
        self.close()


async def fetch_remote_svid(
    tx: Txn, *, kind: str, audiences: Sequence[str]
) -> dict[str, object]:
    """Fetch a remote SVID for the given transaction and kind."""

    if kind == "x509":
        if tx.kind != "uds" or not tx.uds_path:
            raise WorkloadClientError(
                "Unix domain socket endpoint required for x509 SVID"
            )
        with UnixWorkloadClient(tx.uds_path) as client:
            svid = client.fetch_x509_svid(aud=audiences)
        expires_at = int(svid.expires_at.timestamp())
        return {
            "spiffe_id": svid.spiffe_id(),
            "kind": "x509",
            "not_before": max(expires_at - 3600, 0),
            "not_after": expires_at,
            "audiences": tuple(audiences),
            "material": b"".join(cert.public_bytes() for cert in svid.cert_chain),
            "bundle_id": None,
        }

    if kind in {"jwt", "cwt"}:
        if tx.http is None:
            raise WorkloadClientError("HTTP transport required for JWT/CWT SVID fetch")
        path = "/workload/jwtsvid" if kind == "jwt" else "/workload/cwtsvid"
        response = await tx.http.post(path, json={"aud": list(audiences)})
        response.raise_for_status()
        data = response.json()
        spiffe_id = data.get("spiffe_id")
        if not spiffe_id:
            raise WorkloadClientError("Missing spiffe_id in workload response")

        token_key = "jwt" if kind == "jwt" else "cwt"
        token = data.get(token_key)
        if not token:
            raise WorkloadClientError(
                f"Missing {token_key} payload in workload response"
            )
        return {
            "spiffe_id": spiffe_id,
            "kind": kind,
            "not_before": data.get("nbf", 0),
            "not_after": data.get("exp", data.get("expires_at", 0)),
            "audiences": tuple(data.get("aud", audiences)),
            "material": token.encode("utf-8"),
            "bundle_id": data.get("bundle_id"),
        }

    raise WorkloadClientError(f"Unsupported SVID kind: {kind}")


def _coerce_cert_chain(data: dict) -> Tuple[_Certificate, ...]:
    raw_chain = (
        data.get("cert_chain_der")
        or data.get("cert_chain")
        or data.get("chain_der")
        or data.get("chain")
        or data.get("cert_chain_pem")
    )
    if raw_chain is None:
        raise WorkloadClientError("Certificate chain missing from workload response")

    if isinstance(raw_chain, (bytes, bytearray, str)):
        items: Iterable[bytes | str] = [raw_chain]
    else:
        items = raw_chain

    chain: list[_Certificate] = []
    for item in items:
        if isinstance(item, bytes):
            chain.append(_Certificate(bytes(item)))
            continue
        if not isinstance(item, str):
            raise WorkloadClientError("Unsupported certificate payload type")
        token = item.strip()
        if token.startswith("-----BEGIN"):
            chain.append(_Certificate(token.encode("utf-8")))
            continue
        chain.append(_Certificate(_decode_text_token(token)))

    if not chain:
        raise WorkloadClientError("Certificate chain is empty")

    return tuple(chain)


def _decode_text_token(token: str) -> bytes:
    try:
        return base64.b64decode(token, validate=True)
    except (binascii.Error, ValueError):
        try:
            return bytes.fromhex(token)
        except ValueError as exc:  # pragma: no cover - defensive
            raise WorkloadClientError("Unable to decode certificate token") from exc


def _coerce_expires_at(data: dict) -> datetime:
    for key in ("expires_at", "exp", "not_after"):
        if key in data:
            raw = data[key]
            break
    else:
        return datetime.fromtimestamp(0, tz=timezone.utc)

    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw), tz=timezone.utc)

    if isinstance(raw, str):
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return datetime.fromtimestamp(float(raw), tz=timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    raise WorkloadClientError("Unsupported expires_at payload type")
