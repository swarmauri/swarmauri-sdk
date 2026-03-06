from typing import Any, Mapping
class StatusDetailError(Exception):
    def __init__(self, status_code:int, detail:Any="", headers:Mapping[str,str]|None=None):
        super().__init__(detail); self.status_code=int(status_code); self.detail=detail; self.headers=dict(headers or {})
class HTTPException(StatusDetailError):
    pass
