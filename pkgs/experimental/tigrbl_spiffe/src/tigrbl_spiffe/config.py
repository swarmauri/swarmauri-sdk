from __future__ import annotations
from dataclasses import dataclass
from .adapters import Endpoint

@dataclass
class SpiffeConfig:
    workload_endpoint: Endpoint
    server_endpoint: Endpoint

@dataclass
class SpireServerConfig:
    server_endpoint: Endpoint
    default_td: str = "example.org"
    timeout_s: float = 5.0
