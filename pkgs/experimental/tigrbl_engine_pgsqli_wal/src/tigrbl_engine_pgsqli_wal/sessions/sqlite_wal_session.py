from __future__ import annotations

from typing import TypeAlias
from sqlalchemy.orm import Session as _SASession

SqliteWALSession: TypeAlias = _SASession
