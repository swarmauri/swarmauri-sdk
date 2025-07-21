from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class APIKeyOut(BaseModel):
    id: UUID
    label: Optional[str]
    prefix: str
    scopes: List[str]
    expires_at: datetime
    revoked_at: Optional[datetime]

    class Config:
        from_attributes = True
