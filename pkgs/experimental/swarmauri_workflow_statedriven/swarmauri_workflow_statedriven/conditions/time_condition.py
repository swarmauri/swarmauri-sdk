# File: swarmauri/workflows/conditions/time_condition.py

from datetime import datetime, time
from typing import Dict, Any
from swarmauri_workflow_statedriven.conditions.base import Condition


class TimeWindowCondition(Condition):
    """
    File: swarmauri/workflows/conditions/time_condition.py
    Class: TimeWindowCondition

    A condition that is satisfied if the current UTC time falls within
    the specified start_time and end_time window.
    """

    def __init__(self, start_time: time, end_time: time):
        """
        File: swarmauri/workflows/conditions/time_condition.py
        Class: TimeWindowCondition
        Method: __init__

        Args:
            start_time: beginning of the allowed time window (UTC)
            end_time: end of the allowed time window (UTC)
        """
        self.start_time = start_time
        self.end_time = end_time

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: swarmauri/workflows/conditions/time_condition.py
        Class: TimeWindowCondition
        Method: evaluate

        Check whether the current UTC time is between start_time and end_time.
        Handles windows that wrap past midnight.

        Args:
            state: current workflow state (ignored for this condition)

        Returns:
            True if now ∈ [start_time, end_time], False otherwise.
        """
        now = datetime.utcnow().time()
        if self.start_time <= self.end_time:
            return self.start_time <= now <= self.end_time
        # Window wraps midnight
        return now >= self.start_time or now <= self.end_time
