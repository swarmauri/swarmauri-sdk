from pydantic import BaseModel

from swarmauri_core.measurements.IThreshold import IThreshold


class MeasurementThresholdMixin(IThreshold, BaseModel):
    k: int
