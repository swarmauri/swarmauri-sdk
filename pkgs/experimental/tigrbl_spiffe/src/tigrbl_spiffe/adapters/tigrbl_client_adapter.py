from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
import httpx

@dataclass(frozen=True)
class Endpoint:
    scheme: Literal["uds","http","https","grpc"]
    address: str
    timeout_s: float = 5.0

@dataclass
class Txn:
    kind: Literal["uds","http","https","grpc"]
    uds_path: Optional[str] = None
    http: Optional[httpx.AsyncClient] = None

class TigrblClientAdapter:
    async def for_endpoint(self, ep: Endpoint) -> Txn:
        if ep.scheme == "uds":
            return Txn(kind="uds", uds_path=ep.address.replace("unix://","",1))
        if ep.scheme in {"http","https"}:
            return Txn(kind=ep.scheme, http=httpx.AsyncClient(base_url=ep.address, timeout=ep.timeout_s))
        if ep.scheme == "grpc":
            return Txn(kind="grpc")
        raise ValueError(f"Unsupported scheme: {ep.scheme}")
