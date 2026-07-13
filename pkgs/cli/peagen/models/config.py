from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Config(BaseModel):
    output_dir: Optional[str] = Field(default=None)
