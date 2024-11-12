import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    status = report.outcome  # 'passed', 'failed', 'skipped', etc.
    
    if status == "failed":
        return "F", "Custom failure", f"Test failed: {report.longrepr}"
    elif status == "skipped":
        return "S", "Custom skipped", f"Test skipped: {report.longrepr}"
    
    return status[0].upper(), report.nodeid, report.longrepr
