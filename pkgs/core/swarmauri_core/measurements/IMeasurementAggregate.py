from typing import List, Any
from abc import ABC, abstractmethod

class IMeasurementAggregate(ABC):

    @abstractmethod
    def add_measurement(self, measurement: Any) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset or clear the measurement's current state, starting fresh as if no data had been processed.
        This is useful for measurements that might aggregate or average data over time and need to be reset.
        """
        pass