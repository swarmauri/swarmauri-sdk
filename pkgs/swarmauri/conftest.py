import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    status = report.outcome  # 'passed', 'failed', 'skipped', etc.
    
    if status == "failed":
        return status, "Custom failure", (f"Test failed: {report.longrepr}", {"red": True})
    elif status == "skipped":
        return status, "Custom skipped", f"Test skipped: {report.longrepr}", {"yellow": True})
    
    return status, report.nodeid, report.longrepr
