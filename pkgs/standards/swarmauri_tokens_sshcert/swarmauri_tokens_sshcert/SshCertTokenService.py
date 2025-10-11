from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Union,
)

from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider


@dataclass(frozen=True)
class _MintParams:
    cert_type: Literal["user", "host"]
    principals: Sequence[str]
    key_id: str
    serial: Optional[int]
    valid_after: Optional[int]
    valid_before: Optional[int]
    critical_options: Dict[str, str]
    extensions: Dict[str, Optional[str]]


_SSH_CERT_PREFIXES = (
    "ssh-ed25519-cert-v01@openssh.com ",
    "ssh-rsa-cert-v01@openssh.com ",
    "ecdsa-sha2-nistp256-cert-v01@openssh.com ",
    "ecdsa-sha2-nistp384-cert-v01@openssh.com ",
    "ecdsa-sha2-nistp521-cert-v01@openssh.com ",
)

_FINGERPRINT_RE = re.compile(r"SHA256:([A-Za-z0-9+/=]+)")
_SIGNED_BY_RE = re.compile(r"Signed by .* \(SHA256:([A-Za-z0-9+/=]+)\)")
_VALID_AFTER_RE = re.compile(r"Valid:\s+from\s+([0-9-:TZ ]+)\s+to\s+([0-9-:TZ ]+)")
_PRINCIPALS_RE = re.compile(r"Principals:\s+(.+)")
_KEY_ID_RE = re.compile(r"Key ID:\s+(.+)")
_SERIAL_RE = re.compile(r"Serial:\s+(\d+)")
_TYPE_LINE_RE = re.compile(r"Type:\s+(\w+)\s+certificate")


def _require_ssh_keygen() -> None:
    try:
        subprocess.run(
            ["ssh-keygen", "-h"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:  # pragma: no cover
        raise RuntimeError("ssh-keygen not found on PATH; install OpenSSH client tools")


def _write_temp(data: Union[str, bytes], *, mode: int = 0o600, suffix: str = "") -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        if isinstance(data, str):
            data = data.encode("utf-8")
        tmp.write(data)
        tmp.flush()
        os.fchmod(tmp.fileno(), mode)
        return tmp.name
    finally:
        tmp.close()


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _del(file_path: str) -> None:
    try:
        os.remove(file_path)
    except Exception:
        pass


def _fp_of_public(pub_text: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as pub:
        pub.write(pub_text.encode("utf-8"))
        pub.flush()
        pub_path = pub.name
    try:
        out = subprocess.check_output(["ssh-keygen", "-lf", pub_path], text=True)
        m = _FINGERPRINT_RE.search(out)
        if not m:
            raise RuntimeError("Failed to parse fingerprint from ssh-keygen -lf output")
        return m.group(1)
    finally:
        _del(pub_path)


def _format_validity_v_spec(
    valid_after: Optional[int], valid_before: Optional[int]
) -> str:
    if valid_after and valid_before:
        fa = time.gmtime(int(valid_after))
        fb = time.gmtime(int(valid_before))

        def fmt(tm: time.struct_time) -> str:
            return f"{tm.tm_year:04d}{tm.tm_mon:02d}{tm.tm_mday:02d}:{tm.tm_hour:02d}{tm.tm_min:02d}{tm.tm_sec:02d}"

        return f"{fmt(fa)}-{fmt(fb)}"
    return "+1h"


def _parse_cert_listing(text: str) -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    lines = text.splitlines()
    m = _TYPE_LINE_RE.search(text)
    if m:
        info["cert_type"] = m.group(1).lower()

    m = _KEY_ID_RE.search(text)
    if m:
        info["key_id"] = m.group(1).strip().strip('"')

    m = _SERIAL_RE.search(text)
    if m:
        info["serial"] = int(m.group(1))

    m = _PRINCIPALS_RE.search(text)
    if m:
        principals = [p.strip() for p in m.group(1).split(",") if p.strip()]
        info["principals"] = principals

    m = _VALID_AFTER_RE.search(text)
    if m:
        info["valid_after_str"] = m.group(1).strip()
        info["valid_before_str"] = m.group(2).strip()

    m = _SIGNED_BY_RE.search(text)
    if m:
        info["signed_by_sha256"] = m.group(1)
    else:
        for line in lines:
            if line.strip().startswith("Signing CA:"):
                m2 = _FINGERPRINT_RE.search(line)
                if m2:
                    info["signed_by_sha256"] = m2.group(1)
                break

    crit: Dict[str, str] = {}
    exts: Dict[str, Optional[str]] = {}
    state = None
    for line in lines:
        if line.strip().startswith("Critical Options:"):
            state = "crit"
            continue
        if line.strip().startswith("Extensions:"):
            state = "exts"
            continue
        if state == "crit" and line.strip().startswith("\t"):
            t = line.strip().lstrip("\t")
            if " " in t:
                k, v = t.split(" ", 1)
                crit[k] = v.strip().strip('"')
            else:
                crit[t] = ""
        if state == "exts" and line.strip().startswith("\t"):
            t = line.strip().lstrip("\t")
            if "=" in t:
                k, v = t.split("=", 1)
                exts[k] = v.strip().strip('"')
            else:
                exts[t] = None
    if crit:
        info["critical_options"] = crit
    if exts:
        info["extensions"] = exts
    return info


class SshCertTokenService(TokenServiceBase):
    type: Literal["SshCertTokenService"] = "SshCertTokenService"

    def __init__(
        self,
        ca_key_provider: IKeyProvider,
        *,
        ca_kid: str,
        ca_key_version: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._kp = ca_key_provider
        self._ca_kid = ca_kid
        self._ca_ver = ca_key_version

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "formats": ("SSH-CERT",),
            "algs": ("ssh-ed25519", "ssh-rsa", "ecdsa-sha2-nistp256"),
        }

    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: Optional[str] = None,
        key_version: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = None,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[Union[str, list[str]]] = None,
        scope: Optional[str] = None,
    ) -> str:
        _require_ssh_keygen()
        subj_pub: str = claims.get("subject_pub") or claims.get("subject_public")
        if not isinstance(subj_pub, str) or not subj_pub.strip():
            raise ValueError("claims['subject_pub'] (OpenSSH public key) is required")
        if not subj_pub.strip().endswith("\n"):
            subj_pub = subj_pub.strip() + "\n"

        params = _MintParams(
            cert_type=(claims.get("cert_type") or "user"),
            principals=tuple(claims.get("principals") or []),
            key_id=(claims.get("key_id") or claims.get("kid") or "ssh-cert"),
            serial=claims.get("serial"),
            valid_after=claims.get("valid_after"),
            valid_before=claims.get("valid_before"),
            critical_options=dict(claims.get("critical_options") or {}),
            extensions=dict(claims.get("extensions") or {}),
        )
        if params.cert_type not in ("user", "host"):
            raise ValueError("claims['cert_type'] must be 'user' or 'host'")
        if not params.principals:
            raise ValueError("claims['principals'] is required and must be non-empty")

        ca_ref = await self._kp.get_key(self._ca_kid, self._ca_ver, include_secret=True)
        if not ca_ref.material:
            raise RuntimeError(
                "CA private key material is not exportable under current policy"
            )
        ca_priv_path = _write_temp(ca_ref.material, mode=0o600, suffix=".pem")

        subj_pub_path = _write_temp(subj_pub, mode=0o600, suffix=".pub")
        cert_out_path = (
            subj_pub_path[:-4] + "-cert.pub"
            if subj_pub_path.endswith(".pub")
            else subj_pub_path + "-cert.pub"
        )

        v_spec = _format_validity_v_spec(params.valid_after, params.valid_before)
        if not (params.valid_after and params.valid_before) and lifetime_s:
            if lifetime_s % 60 == 0:
                v_spec = f"+{int(lifetime_s / 60)}m"
            else:
                v_spec = f"+{int(lifetime_s)}s"

        cmd = [
            "ssh-keygen",
            "-s",
            ca_priv_path,
            "-I",
            params.key_id,
            "-V",
            v_spec,
            "-z",
            str(params.serial if params.serial is not None else int(time.time())),
        ]

        if params.cert_type == "user":
            cmd += ["-n", ",".join(params.principals)]
        else:
            cmd += ["-h", "-n", ",".join(params.principals)]

        for k, v in params.critical_options.items():
            if v is None or v == "":
                cmd += ["-O", k]
            else:
                cmd += ["-O", f"{k}={v}"]

        for k, v in params.extensions.items():
            if v is None or v == "":
                cmd += ["-O", k]
            else:
                cmd += ["-O", f"{k}={v}"]

        cmd.append(subj_pub_path)

        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            cert_line = _read_file(cert_out_path).decode("utf-8").strip()
            if not any(cert_line.startswith(p) for p in _SSH_CERT_PREFIXES):
                raise RuntimeError("Unexpected certificate format from ssh-keygen")
            return cert_line
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ssh-keygen failed: {e.output.strip()}") from e
        finally:
            _del(subj_pub_path)
            _del(cert_out_path)
            _del(ca_priv_path)

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[Union[str, list[str]]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        _require_ssh_keygen()

        cert_path = _write_temp(
            token if token.endswith("\n") else token + "\n",
            mode=0o600,
            suffix="-cert.pub",
        )

        ca_ref = await self._kp.get_key(
            self._ca_kid, self._ca_ver, include_secret=False
        )
        if not ca_ref.public:
            raise RuntimeError(
                "CA public key not available from provider for verification"
            )
        ca_pub_text = (
            ca_ref.public.decode("utf-8")
            if isinstance(ca_ref.public, (bytes, bytearray))
            else ca_ref.public
        )
        ca_fp = _fp_of_public(ca_pub_text)

        try:
            out = subprocess.check_output(
                ["ssh-keygen", "-Lf", cert_path], text=True, stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            _del(cert_path)
            raise ValueError(
                f"Invalid SSH certificate (ssh-keygen -Lf failed): {e.output.strip()}"
            ) from e

        info = _parse_cert_listing(out)

        signed_by = info.get("signed_by_sha256")
        if not signed_by:
            _del(cert_path)
            raise ValueError(
                "Unable to determine signing CA fingerprint from certificate"
            )
        if signed_by != ca_fp:
            _del(cert_path)
            raise ValueError("Certificate signer does not match configured CA")

        def _parse_ts(s: str) -> int:
            s = s.replace("T", " ").strip()
            tm = time.strptime(s, "%Y-%m-%d %H:%M:%S")
            return int(time.mktime(time.gmtime(time.mktime(tm))))

        now = int(time.time())
        va = info.get("valid_after_str")
        vb = info.get("valid_before_str")
        if va and vb:
            va_epoch = _parse_ts(va)
            vb_epoch = _parse_ts(vb)
            info["valid_after"] = va_epoch
            info["valid_before"] = vb_epoch
            if now + leeway_s < va_epoch:
                _del(cert_path)
                raise ValueError("Certificate not yet valid")
            if vb_epoch and now > vb_epoch + leeway_s:
                _del(cert_path)
                raise ValueError("Certificate expired")

        if audience is not None:
            principals = set(info.get("principals", []))
            if isinstance(audience, str):
                aud_ok = audience in principals
            else:
                aud_ok = any(a in principals for a in audience)
            if not aud_ok:
                _del(cert_path)
                raise ValueError("Audience/principal mismatch")

        info["active"] = True
        _del(cert_path)
        return info

    async def jwks(self) -> dict:
        return {"keys": []}
