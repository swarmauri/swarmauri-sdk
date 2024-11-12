import pytest
import os
import inspect

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.failed:
        file_path = inspect.getfile(item.function)
        line_number = inspect.getsourcelines(item.function)[1]

        file_link = f"file://{os.path.abspath(file_path)}:{line_number}"

        result.longrepr = f"{result.longrepr}\n\nCustom Error: View the failing test here -> {file_link}"
