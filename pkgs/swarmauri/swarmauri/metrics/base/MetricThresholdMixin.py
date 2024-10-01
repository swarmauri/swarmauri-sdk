from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel
from swarmauri_core.metrics.IThreshold import IThreshold

class MetricThresholdMixin(IThreshold, BaseModel):
    k: int
    