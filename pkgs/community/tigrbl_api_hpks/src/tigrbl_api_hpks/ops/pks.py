"""Reusable HPKS operation helpers built on top of Tigrbl handlers."""

from __future__ import annotations

import base64
import binascii
import datetime as dt
import hashlib
import inspect
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Mapping, Sequence

import pgpy
from tigrbl import op_ctx

from ..tables import OpenPGPKey


def _stable_unique(values: Iterable[str]) -> list[str]:
    """Return a list containing the first occurrence of each non-empty value."""

    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _format_userid(uid: Any) -> str:
    """Render a :class:`PGPUID` into a canonical string representation."""

    name = getattr(uid, "name", None)
    comment = getattr(uid, "comment", None)
    email = getattr(uid, "email", None)
    parts: list[str] = []
    if name:
        parts.append(str(name))
    if comment:
        parts.append(f"({comment})")
    if email:
        parts.append(f"<{email}>")
    if parts:
        return " ".join(parts)
    fallback = getattr(uid, "userid", None)
    if fallback:
        return str(fallback)
    return str(uid)


def _iter_revocation_signatures(key: Any) -> Iterator[Any]:
    """Safely iterate over revocation signatures exposed by a key object."""

    revocations = getattr(key, "revocation_signatures", None)
    if revocations is None:
        return iter(())
    if isinstance(revocations, Iterator):
        return revocations
    try:
        return iter(revocations)
    except TypeError:
        return iter(())


def _extract_revocation_state(key: Any) -> tuple[bool, dt.datetime | None]:
    """Determine the revocation status and timestamp for a parsed key."""

    raw_revoked = getattr(key, "is_revoked", False)
    revoked = raw_revoked is True if isinstance(raw_revoked, bool) else False
    revoked_at = _ensure_tzaware(getattr(key, "revocation_date", None))
    if revoked_at is not None and not revoked:
        revoked = True

    latest: dt.datetime | None = revoked_at if revoked_at is not None else None
    if revoked and revoked_at is not None:
        return revoked, revoked_at

    for signature in list(_iter_revocation_signatures(key)):
        if signature is None:
            continue
        revoked = True
        created = getattr(signature, "created", None) or getattr(
            signature, "creation_time", None
        )
        if created is None:
            continue
        created_dt = _ensure_tzaware(created)
        if created_dt is None:
            continue
        if latest is None or created_dt > latest:
            latest = created_dt
    return revoked, latest


@dataclass(slots=True)
class ParsedKey:
    """Structured metadata extracted from a PGPy key object."""

    fingerprint: str
    key_id: str
    prefix: str
    ascii_armored: str
    binary: bytes
    uids: list[str]
    emails: list[str]
    email_hashes: list[str]
    revoked: bool
    revoked_at: dt.datetime | None
    algorithm: str | None
    bits: int | None
    primary_uid: str | None
    version: int | None


_HEX_CHARS = set("0123456789ABCDEF")


def _is_hex(value: str) -> bool:
    if not value:
        return False
    return all(ch in _HEX_CHARS for ch in value)


def _normalize_fingerprint(value: str) -> str:
    stripped = value.strip().replace(" ", "")
    if stripped.lower().startswith("0x"):
        stripped = stripped[2:]
    return stripped.upper()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_email(email: str) -> str:
    return hashlib.sha1(_normalize_email(email).encode("utf-8")).hexdigest()


def _coerce_datetime(value: str) -> dt.datetime:
    dt_obj = dt.datetime.fromisoformat(value)
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=dt.timezone.utc)
    return dt_obj


def _coerce_bits(value: Any) -> int | None:
    """Normalize key-size data from PGPy into a numeric bit count."""

    if value is None:
        return None

    # Try direct integer conversion first for simple types.
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        coerced = None
    else:
        return coerced

    # Fall back to inspecting common attributes exposed by enum-like objects.
    for attr in ("key_size", "size"):
        candidate = getattr(value, attr, None)
        if candidate is None:
            continue
        try:
            return int(candidate)
        except (TypeError, ValueError):
            continue

    return None


def _ensure_tzaware(value: dt.datetime | None) -> dt.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.timezone.utc)
    return value


def _coerce_rest(rest: Any) -> bytes | None:
    if rest is None:
        return None
    if isinstance(rest, (bytes, bytearray, memoryview)):
        return bytes(rest)
    if isinstance(rest, str):
        return rest.encode("utf-8")
    try:
        return bytes(rest)
    except (TypeError, ValueError):
        return None


def _slice_consumed(remaining: bytes, rest: bytes | None) -> bytes:
    if not remaining:
        return b""
    if not rest:
        return bytes(remaining)
    if len(rest) >= len(remaining):
        return bytes(remaining)
    consumed_len = len(remaining) - len(rest)
    return bytes(remaining[:consumed_len])


def _looks_ascii_armored(blob: bytes) -> bool:
    return blob.lstrip().startswith(b"-----BEGIN ")


def _decode_ascii_armor(blob: bytes) -> bytes:
    text = blob.decode("utf-8")
    lines = text.splitlines()
    body_lines: list[str] = []
    collecting = False
    for line in lines:
        if line.startswith("-----BEGIN "):
            collecting = False
            continue
        if line.startswith("-----END "):
            break
        if not collecting:
            if line.strip() == "":
                collecting = True
            continue
        stripped = line.strip()
        if not stripped:
            continue
        body_lines.append(stripped)
    if body_lines and body_lines[-1].startswith("="):
        body_lines.pop()
    payload = "".join(body_lines)
    if not payload:
        return b""
    return base64.b64decode(payload)


def _collect_keys(blob: bytes) -> list[tuple[pgpy.PGPKey, bytes]]:
    remaining: bytes = bytes(blob)
    keys: list[tuple[pgpy.PGPKey, bytes]] = []
    while remaining:
        key, rest = pgpy.PGPKey.from_blob(remaining)
        if key is None:
            break
        if getattr(key, "is_public", False) is False and getattr(key, "pubkey", None):
            key = key.pubkey
        rest_bytes = _coerce_rest(rest)
        consumed = _slice_consumed(remaining, rest_bytes)
        keys.append((key, consumed))
        if not rest_bytes:
            break
        if rest_bytes == remaining:
            break
        remaining = rest_bytes
    return keys


def _parse_blob(blob: bytes) -> list[ParsedKey]:
    try:
        keys = _collect_keys(blob)
    except (pgpy.errors.PGPError, ValueError) as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to parse OpenPGP material: {exc}") from exc

    parsed: list[ParsedKey] = []
    for key, raw_blob in keys:
        fingerprint = _normalize_fingerprint(key.fingerprint)
        key_id = fingerprint[-16:]
        prefix = fingerprint[:16]
        ascii_armored: str
        binary_blob: bytes
        ascii_candidate: str | None = None
        if raw_blob and _looks_ascii_armored(raw_blob):
            try:
                ascii_candidate = raw_blob.decode("utf-8")
            except UnicodeDecodeError:
                ascii_candidate = None

        if (
            ascii_candidate
            and "-----BEGIN PGP PUBLIC KEY BLOCK-----" in ascii_candidate
        ):
            ascii_armored = ascii_candidate
            try:
                binary_blob = _decode_ascii_armor(raw_blob)
            except (binascii.Error, ValueError):
                binary_blob = bytes(key)
        else:
            ascii_armored = str(key)
            binary_blob = bytes(key)
        uids = _stable_unique(_format_userid(uid) for uid in key.userids)
        emails = _stable_unique(
            _normalize_email(getattr(uid, "email", ""))
            for uid in key.userids
            if getattr(uid, "email", None)
        )
        email_hashes = sorted({_hash_email(email) for email in emails})
        revoked, revoked_at = _extract_revocation_state(key)
        algorithm = None
        if getattr(key, "key_algorithm", None) is not None:
            algo = key.key_algorithm
            algorithm = getattr(algo, "name", str(algo))
        bits = _coerce_bits(getattr(key, "key_size", None))
        primary_uid = (
            str(key.primary_uid)
            if getattr(key, "primary_uid", None)
            else (uids[0] if uids else None)
        )
        version = None
        if getattr(key, "key_packet", None) is not None:
            version = getattr(key.key_packet, "version", None)
            if version is not None:
                try:
                    version = int(version)
                except (TypeError, ValueError):
                    version = None
        parsed.append(
            ParsedKey(
                fingerprint=fingerprint,
                key_id=key_id,
                prefix=prefix,
                ascii_armored=ascii_armored,
                binary=binary_blob,
                uids=uids,
                emails=sorted(set(emails)),
                email_hashes=email_hashes,
                revoked=revoked,
                revoked_at=revoked_at,
                algorithm=algorithm,
                bits=bits,
                primary_uid=primary_uid,
                version=version,
            )
        )
    return parsed


async def _list_all(db: Any) -> list[OpenPGPKey]:
    ctx = {"db": db, "payload": {}}
    return await OpenPGPKey.handlers.list.core(ctx)  # type: ignore[no-any-return]


async def lookup_by_fingerprint(*, db: Any, fingerprint: str) -> OpenPGPKey | None:
    normalized = _normalize_fingerprint(fingerprint)
    ctx = {"db": db, "payload": {"fingerprint__eq": normalized}}
    rows = await OpenPGPKey.handlers.list.core(ctx)
    return rows[0] if rows else None


async def lookup_by_keyid(*, db: Any, key_id: str) -> OpenPGPKey | None:
    normalized = _normalize_fingerprint(key_id)[-16:]
    ctx = {"db": db, "payload": {"key_id__eq": normalized}}
    rows = await OpenPGPKey.handlers.list.core(ctx)
    return rows[0] if rows else None


async def lookup_by_email_hash(*, db: Any, email_hash: str) -> OpenPGPKey | None:
    hashed = email_hash.lower()
    rows = await _list_all(db)
    for row in rows:
        if any(h.lower() == hashed for h in row.email_hashes or []):
            return row
    return None


async def search_index(*, db: Any, search: str) -> list[OpenPGPKey]:
    query = search.strip()
    if not query:
        return []
    normalized = _normalize_fingerprint(query)
    # Prefer exact fingerprint or key ID matches.
    if len(normalized) in (40, 64) and _is_hex(normalized):
        match = await lookup_by_fingerprint(db=db, fingerprint=normalized)
        return [match] if match else []
    if len(normalized) == 16 and _is_hex(normalized):
        match = await lookup_by_keyid(db=db, key_id=normalized)
        return [match] if match else []

    rows = await _list_all(db)
    lowered = query.lower()
    matches: list[OpenPGPKey] = []
    for row in rows:
        if lowered in row.fingerprint.lower():
            matches.append(row)
            continue
        if any(lowered in (uid or "").lower() for uid in row.uids or []):
            matches.append(row)
            continue
        if any(lowered in email for email in row.emails or []):
            matches.append(row)
    return matches


def _merge_lists(existing: Sequence[str] | None, incoming: Iterable[str]) -> list[str]:
    merged = set(existing or [])
    merged.update(incoming)
    return sorted(merged)


async def _merge_parsed_key(*, db: Any, parsed: ParsedKey) -> OpenPGPKey:
    existing = await lookup_by_fingerprint(db=db, fingerprint=parsed.fingerprint)
    payload: dict[str, Any] = {
        "fingerprint": parsed.fingerprint,
        "key_id": parsed.key_id,
        "fingerprint_prefix": parsed.prefix,
        "ascii_armored": parsed.ascii_armored,
        "binary": parsed.binary,
        "uids": parsed.uids,
        "emails": parsed.emails,
        "email_hashes": parsed.email_hashes,
        "revoked": parsed.revoked,
        "revoked_at": parsed.revoked_at,
        "algorithm": parsed.algorithm,
        "bits": parsed.bits,
        "primary_uid": parsed.primary_uid,
        "version": parsed.version,
    }
    if existing is not None:
        payload["uids"] = parsed.uids or _stable_unique(existing.uids or [])
        payload["emails"] = parsed.emails or _stable_unique(existing.emails or [])
        payload["email_hashes"] = parsed.email_hashes or _stable_unique(
            existing.email_hashes or []
        )
        payload["ascii_armored"] = parsed.ascii_armored or existing.ascii_armored
        payload["binary"] = parsed.binary or existing.binary
        if existing.revoked:
            payload["revoked"] = True
            payload["revoked_at"] = existing.revoked_at
        elif parsed.revoked:
            payload["revoked"] = True
            payload["revoked_at"] = parsed.revoked_at or existing.revoked_at
        else:
            payload["revoked"] = False
            payload["revoked_at"] = None
        payload["algorithm"] = parsed.algorithm or existing.algorithm
        payload["bits"] = parsed.bits or existing.bits
        payload["primary_uid"] = parsed.primary_uid or existing.primary_uid
        payload["version"] = parsed.version or existing.version
    ctx = {"db": db, "payload": payload}
    record = await OpenPGPKey.handlers.merge.handler(ctx)
    await _commit_session(db)
    return record


async def _commit_session(db: Any) -> None:
    commit = getattr(db, "commit", None)
    if commit is None or not callable(commit):
        return
    result = commit()
    if inspect.isawaitable(result):
        await result


async def ingest_blob(*, db: Any, blob: bytes) -> dict[str, list[str]]:
    parsed = _parse_blob(blob)
    if not parsed:
        raise ValueError("No OpenPGP certificates found in payload")
    inserted: list[str] = []
    updated: list[str] = []
    for entry in parsed:
        existing = await lookup_by_fingerprint(db=db, fingerprint=entry.fingerprint)
        await _merge_parsed_key(db=db, parsed=entry)
        if existing is None:
            inserted.append(entry.fingerprint)
        else:
            updated.append(entry.fingerprint)
    return {"inserted": inserted, "updated": updated, "ignored": []}


async def ingest_armored(*, db: Any, armored: str) -> dict[str, list[str]]:
    return await ingest_blob(db=db, blob=armored.encode("utf-8"))


async def ingest_binary(*, db: Any, bundle: bytes) -> dict[str, list[str]]:
    return await ingest_blob(db=db, blob=bundle)


def _coerce_bytes(value: Any) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        try:
            return base64.b64decode(value)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                "Binary payload must be base64-encoded when provided as a string"
            ) from exc
    raise ValueError("Unsupported binary payload type")


async def merge_json_payload(
    *, db: Any, fingerprint: str, payload: Mapping[str, Any]
) -> OpenPGPKey:
    normalized = _normalize_fingerprint(fingerprint)
    armored = payload.get("armored") or payload.get("ascii_armored")
    binary_blob = payload.get("binary")
    parsed_entries: list[ParsedKey] = []
    if armored:
        parsed_entries = _parse_blob(str(armored).encode("utf-8"))
    elif binary_blob is not None:
        parsed_entries = _parse_blob(_coerce_bytes(binary_blob))
    if parsed_entries:
        entry = parsed_entries[0]
        if entry.fingerprint != normalized:
            raise ValueError("Fingerprint mismatch between path and payload")
        return await _merge_parsed_key(db=db, parsed=entry)

    existing = await lookup_by_fingerprint(db=db, fingerprint=normalized)
    if existing is None:
        raise ValueError("No key material supplied for new fingerprint")

    flags = payload.get("flags") or {}
    revoked = payload.get("revoked")
    if revoked is None and "revoked" in flags:
        revoked = flags.get("revoked")
    revoked_at_raw = payload.get("revoked_at") or flags.get("revoked_at")
    algorithm = payload.get("algo") or payload.get("algorithm") or flags.get("algo")
    bits_value = _coerce_bits(payload.get("bits") or flags.get("bits"))
    primary_uid = payload.get("primary_uid") or flags.get("primary_uid")
    merged_payload: dict[str, Any] = {
        "fingerprint": existing.fingerprint,
        "key_id": existing.key_id,
        "fingerprint_prefix": existing.fingerprint_prefix,
        "ascii_armored": payload.get("ascii_armored") or existing.ascii_armored,
        "binary": existing.binary,
        "uids": _merge_lists(existing.uids, payload.get("uids", [])),
        "emails": _merge_lists(
            existing.emails, [_normalize_email(e) for e in payload.get("emails", [])]
        ),
        "email_hashes": _merge_lists(
            existing.email_hashes, [_hash_email(e) for e in payload.get("emails", [])]
        ),
        "revoked": bool(revoked) if revoked is not None else existing.revoked,
        "revoked_at": _ensure_tzaware(
            _coerce_datetime(revoked_at_raw) if revoked_at_raw else existing.revoked_at
        ),
        "algorithm": algorithm or existing.algorithm,
        "bits": bits_value if bits_value is not None else existing.bits,
        "primary_uid": primary_uid or existing.primary_uid,
        "version": payload.get("version") or existing.version,
    }
    ctx = {"db": db, "payload": merged_payload}
    record = await OpenPGPKey.handlers.merge.handler(ctx)
    await _commit_session(db)
    return record


def render_legacy_index(records: Sequence[OpenPGPKey], *, search: str) -> str:
    total = len(records)
    lines: list[str] = [f"info:{total}:{total}:{search}"]
    for record in records:
        created = int(record.created_at.timestamp()) if record.created_at else 0
        key_id = record.key_id.upper()
        algo = (record.algorithm or "").upper()
        bits = record.bits or 0
        lines.append(f"pub:{algo}:{bits}:{created}::{key_id}:{record.fingerprint}")
        for uid in record.uids or []:
            lines.append(f"uid:{uid}")
    return "\n".join(lines) + "\n"


def to_v2_document(record: OpenPGPKey) -> dict[str, Any]:
    return {
        "version": record.version or 4,
        "fingerprint": record.fingerprint,
        "key_id": record.key_id,
        "fingerprint_prefix": record.fingerprint_prefix,
        "uids": list(record.uids or []),
        "emails": list(record.emails or []),
        "revoked": bool(record.revoked),
        "revoked_at": record.revoked_at.isoformat() if record.revoked_at else None,
        "algorithm": record.algorithm,
        "bits": record.bits,
        "primary_uid": record.primary_uid,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


async def prefix_log(*, db: Any, since: dt.datetime) -> list[str]:
    rows = await _list_all(db)
    threshold = _ensure_tzaware(since)
    prefixes: list[str] = []
    for row in rows:
        updated = _ensure_tzaware(row.updated_at)
        if updated and threshold and updated >= threshold:
            prefixes.append(row.fingerprint_prefix)
    return prefixes


@op_ctx(alias="index", target="custom", arity="collection", bind=OpenPGPKey, rest=False)
async def op_index(*, search: str, model=None, ctx=None, **_kw) -> list[OpenPGPKey]:
    db = ctx.get("db") if ctx else None
    if db is None:
        raise ValueError("Database session required")
    return await search_index(db=db, search=search)


@op_ctx(alias="get", target="custom", arity="member", bind=OpenPGPKey, rest=False)
async def op_get(*, search: str, model=None, ctx=None, **_kw) -> OpenPGPKey | None:
    db = ctx.get("db") if ctx else None
    if db is None:
        raise ValueError("Database session required")
    return await lookup_by_fingerprint(db=db, fingerprint=search)


@op_ctx(alias="hget", target="custom", arity="member", bind=OpenPGPKey, rest=False)
async def op_hget(*, search: str, model=None, ctx=None, **_kw) -> OpenPGPKey | None:
    db = ctx.get("db") if ctx else None
    if db is None:
        raise ValueError("Database session required")
    return await lookup_by_email_hash(db=db, email_hash=search)


__all__ = [
    "ParsedKey",
    "ingest_armored",
    "ingest_binary",
    "ingest_blob",
    "lookup_by_email_hash",
    "lookup_by_fingerprint",
    "lookup_by_keyid",
    "merge_json_payload",
    "op_get",
    "op_hget",
    "op_index",
    "prefix_log",
    "render_legacy_index",
    "search_index",
    "to_v2_document",
]
