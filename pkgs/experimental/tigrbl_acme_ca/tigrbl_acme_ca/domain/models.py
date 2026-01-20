from __future__ import annotations
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    processing = "processing"
    valid = "valid"
    invalid = "invalid"


class AuthorizationStatus(str, Enum):
    pending = "pending"
    valid = "valid"
    invalid = "invalid"
    expired = "expired"


class ChallengeStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    valid = "valid"
    invalid = "invalid"
