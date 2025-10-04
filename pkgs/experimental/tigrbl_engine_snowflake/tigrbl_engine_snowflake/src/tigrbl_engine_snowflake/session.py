from __future__ import annotations

from typing import TypeAlias
from sqlalchemy.orm import Session as _SASession

# Explicit alias for consumer typing
SnowflakeSession: TypeAlias = _SASession
