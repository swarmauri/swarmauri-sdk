"""Correlation identifiers carried by live events."""

from typing import Optional

from pydantic import BaseModel


class LiveCorrelation(BaseModel):
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    response_id: Optional[str] = None
    item_id: Optional[str] = None
    call_id: Optional[str] = None
    provider_event_id: Optional[str] = None
