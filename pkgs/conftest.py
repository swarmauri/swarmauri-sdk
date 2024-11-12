import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    if report.failed:
        return "F", "Custom failure message", "Test failed due to XYZ reason"
    return report.status, report.shortrepr, report.longrepr
