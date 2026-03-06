
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, AsyncIterable, Iterable, Optional, Union
@dataclass(frozen=True, slots=True)
class Response:
    status_code: int = 200
    media_type: str = 'application/json'
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b''
    stream: Optional[Union[Iterable[bytes], AsyncIterable[bytes]]] = None
    value: Any = None
    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [(str(k).encode('latin-1'), str(v).encode('latin-1')) for k,v in self.headers.items()]
