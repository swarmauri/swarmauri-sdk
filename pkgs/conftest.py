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
    # Use report.outcome to check the status of the test
    status = report.outcome  # This will be 'passed', 'failed', 'skipped', etc.
    
    # Customize messages based on test status
    if status == "failed":
        return "F", "Custom failure", "Test failed due to XYZ reason"
    elif status == "skipped":
        return "S", "Custom skipped", "Test was skipped for reason ABC"
    
    # Default handling for passed tests
    return status[0].upper(), report.shortrepr, report.longrepr
