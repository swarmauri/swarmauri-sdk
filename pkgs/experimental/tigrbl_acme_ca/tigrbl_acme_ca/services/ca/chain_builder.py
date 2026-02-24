from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ChainBuildResult:
    chain_pem: list[str]


def build_chain(
    leaf_pem: str,
    intermediate_pem: Optional[str] = None,
    root_pem: Optional[str] = None,
) -> ChainBuildResult:
    chain: List[str] = [leaf_pem]
    if intermediate_pem:
        chain.append(intermediate_pem)
    if root_pem:
        chain.append(root_pem)
    return ChainBuildResult(chain_pem=chain)
