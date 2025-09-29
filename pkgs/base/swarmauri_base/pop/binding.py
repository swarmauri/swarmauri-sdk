from __future__ import annotations

from typing import Any, Mapping

from swarmauri_core.pop import BindType, CnfBinding


def normalize_cnf(cnf_claim: Mapping[str, Any]) -> CnfBinding:
    """Normalize cnf claim dictionaries into strongly typed bindings."""

    if "jkt" in cnf_claim:
        return CnfBinding(BindType.JKT, str(cnf_claim["jkt"]))
    if "x5t#S256" in cnf_claim:
        return CnfBinding(BindType.X5T_S256, str(cnf_claim["x5t#S256"]))
    if "cose_key_thumbprint" in cnf_claim:
        return CnfBinding(BindType.COSE_THUMB, str(cnf_claim["cose_key_thumbprint"]))
    raise ValueError("Unsupported cnf claim")


def make_cnf_jkt(jkt_b64u: str) -> dict[str, str]:
    return {"jkt": jkt_b64u}


def make_cnf_x5t(x5t_b64u: str) -> dict[str, str]:
    return {"x5t#S256": x5t_b64u}


def make_cnf_cose(thumb_b64u: str) -> dict[str, str]:
    return {"cose_key_thumbprint": thumb_b64u}
