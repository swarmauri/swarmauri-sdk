from enum import Enum


class WebSocketState(str, Enum):
    NEW = "new"
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    FAILED = "failed"
