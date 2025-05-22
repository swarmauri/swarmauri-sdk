# File: tests/workflows/conditions/test_time_condition.py

import pytest
from datetime import datetime, time
import swarmauri_workflow_statedriven.conditions.time_condition as tc_module
from swarmauri_workflow_statedriven.conditions.time_condition import TimeWindowCondition


class _FixedDateTime:
    """
    Helper to monkeypatch datetime.utcnow() to return a fixed time.
    """

    def __init__(self, fixed_time: time):
        self._fixed = fixed_time

    def utcnow(self):
        # Return a datetime whose .time() is the fixed time
        now = datetime.now()
        return datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=self._fixed.hour,
            minute=self._fixed.minute,
            second=self._fixed.second,
        )


@pytest.mark.unit
def test_within_non_wrapping_window(monkeypatch):
    """
    File: workflows/conditions/time_condition.py
    Class: TimeWindowCondition
    Method: evaluate

    For a window 09:00–17:00, times within are True, outside False.
    """
    # Monkeypatch datetime in module
    fixed = time(12, 0, 0)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))

    cond = TimeWindowCondition(start_time=time(9, 0, 0), end_time=time(17, 0, 0))
    assert cond.evaluate({}) is True

    # Before window
    fixed = time(8, 59, 59)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))
    assert cond.evaluate({}) is False

    # After window
    fixed = time(17, 0, 1)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))
    assert cond.evaluate({}) is False


@pytest.mark.unit
def test_within_wrapping_window(monkeypatch):
    """
    File: workflows/conditions/time_condition.py
    Class: TimeWindowCondition
    Method: evaluate

    For a window that wraps midnight (22:00–02:00), times in late night and early morning are True.
    """
    # Setup wrapping window
    cond = TimeWindowCondition(start_time=time(22, 0, 0), end_time=time(2, 0, 0))

    # Late-night case
    fixed = time(23, 30, 0)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))
    assert cond.evaluate({}) is True

    # Early-morning case
    fixed = time(1, 0, 0)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))
    assert cond.evaluate({}) is True

    # Outside window
    fixed = time(3, 0, 0)
    monkeypatch.setattr(tc_module, "datetime", _FixedDateTime(fixed))
    assert cond.evaluate({}) is False
