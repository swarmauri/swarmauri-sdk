"""Correlation identifiers carried by live events."""


from pydantic import BaseModel


class LiveCorrelation(BaseModel):
    session_id: str | None = None
    turn_id: str | None = None
    response_id: str | None = None
    item_id: str | None = None
    call_id: str | None = None
    provider_event_id: str | None = None
