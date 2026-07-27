from enum import Enum


class LiveSessionState(str, Enum):
    NEW = "new"
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    FAILED = "failed"
