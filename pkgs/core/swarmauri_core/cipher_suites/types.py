from __future__ import annotations

from typing import Any, Mapping, Sequence
from typing import Literal, TypedDict
from typing_extensions import NotRequired

CipherOp = Literal[
    "sign",
    "verify",
    "encrypt",
    "decrypt",
    "wrap",
    "unwrap",
    "seal",
    "unseal",
]

Dialect = Literal[
    "jwa",
    "cose",
    "tls",
    "ssh",
    "ike",
    "cms",
    "xmlsig",
    "pdfsig",
    "fido2",
    "sigstore",
    "provider",
]

Alg = str


class KeyRef(TypedDict, total=False):
    kid: str
    kty: str
    crv: NotRequired[str]
    bits: NotRequired[int]
    version: NotRequired[int]


ParamMapping = Mapping[str, Any]


class OpSupports(TypedDict):
    allowed: Sequence[Alg]
    default: Alg


class Features(TypedDict, total=False):
    suite: str
    version: int
    dialects: Mapping[Dialect, Sequence[Any]]
    ops: Mapping[CipherOp, OpSupports]
    constraints: Mapping[str, Any]
    compliance: Mapping[str, Any]
    lifecycle: Mapping[str, Any]
    notes: Sequence[str]


class NormalizedDescriptor(TypedDict, total=False):
    op: CipherOp
    alg: Alg
    dialect: Dialect
    mapped: Mapping[Dialect, Any]
    params: Mapping[str, Any]
    constraints: Mapping[str, Any]
    policy: Mapping[str, Any]


class LintIssue(TypedDict, total=False):
    level: Literal["error", "warn", "info"]
    code: str
    message: str
    context: NotRequired[Mapping[str, Any]]
