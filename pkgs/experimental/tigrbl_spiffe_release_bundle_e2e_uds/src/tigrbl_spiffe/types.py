from __future__ import annotations
from enum import Enum

class SvidKind(str, Enum):
    x509 = "x509"
    jwt = "jwt"
    cwt = "cwt"
