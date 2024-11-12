import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.failed:
        report.longrepr += "\nCustom Message: Something went wrong."
    return report

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    if report.failed:
        return "F", "Custom failure", "Test failed due to XYZ"
    return report.status, report.shortrepr, report.longrepr
