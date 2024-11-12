import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.failed:
        report.longrepr += "\nCustom Message: Something went wrong."
    return report
