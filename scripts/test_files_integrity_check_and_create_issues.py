"""
This script checks if the test files are present for each python file in the given path.
If the test file is missing or empty, it raises an error.
"""

import logging
import os
import sys
from typing import List
from rag_issue_manager import create_issue, add_comment_to_issue, get_existing_issues


# Define color codes
class LogColors:
    """
    Color codes for log messages.
    """

    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    RED: str = "\033[91m"
    RESET: str = "\033[0m"


class CustomFormatter(logging.Formatter):
    """
    Custom formatter to colorize log messages based on log level.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log messages based on log level.
        """
        if record.levelno == logging.INFO:
            record.msg = f"{LogColors.GREEN}{record.msg}{LogColors.RESET}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{LogColors.YELLOW}{record.msg}{LogColors.RESET}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{LogColors.RED}{record.msg}{LogColors.RESET}"
        return super().format(record)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)


def validate_test_file(
    test_file_path: str, file_path: str, missing_tests: List[dict]
) -> bool:
    """
    Validate the test file for the given python file.
    """
    if not os.path.exists(test_file_path):
        data = format_issue_data(file_path)
        missing_tests.append(data)
        logger.error(f"Missing test file for {file_path}")
        raise FileNotFoundError(f"Missing test file for {file_path}")

    if os.path.getsize(test_file_path) == 0:
        data = format_issue_data(file_path)
        missing_tests.append(data)
        logger.error(f"Test file {test_file_path} is empty for {file_path}")
        raise ValueError(f"Test file {test_file_path} is empty for {file_path}")

    logger.info(f"Test file {test_file_path} exists and is not empty for {file_path}")
    return True


def check_subdir_files(
    subdir_path: str, tests_root: str, missing_tests: List[dict]
) -> None:
    """
    Check the files in the given subdirectory.
    """
    test_file_path = ""
    for file in os.listdir(subdir_path):
        if file.endswith(".py") and file != "__init__.py":
            file_path = os.path.join(subdir_path, file)
            for root, _, test_files in os.walk(tests_root):
                for test_file in test_files:
                    if file.split(".")[0].lower() in test_file.lower():
                        test_file_path = os.path.join(root, test_file)
                        try:
                            validate_test_file(test_file_path, file_path, missing_tests)
                        except FileNotFoundError:
                            continue
                        break
                else:
                    continue
                break
            else:
                data = format_issue_data(file_path)
                missing_tests.append(data)


def format_issue_data(path: str) -> dict:
    """
    Format the data for creating issues based on missing test files.
    """
    parts = path.split("/")
    data = {
        "name": f"{'/'.join(parts[:-2])}/tests/unit/test_{parts[-1].split('.')[0]}.py",
        "path": path,
        "message": "Test file is missing",
    }
    return data


def check_files_integrity(path: str) -> List[dict]:
    """
    Check if the test files are present for each python file in the given path.
    """
    missing_tests: List[dict] = []
    for root, dirs, files in os.walk(path):
        if "tests" not in dirs:
            continue

        for subdir in dirs:
            if subdir == "tests":
                continue

            subdir_path = os.path.join(root, subdir)
            check_subdir_files(subdir_path, os.path.join(root, "tests"), missing_tests)

    if missing_tests:
        logger.info(
            "\n\n==========================Summary of missing test files:===================================\n"
        )
        for missing_test in missing_tests:
            logger.error(f"Missing test file for: {missing_test['path']}")
    else:
        logger.info("All test files are present.")

    return missing_tests


if __name__ == "__main__":
    missing_tests_data = check_files_integrity("pkgs")

    for test_data in missing_tests_data:
        existing_issues = get_existing_issues()

        issue_title = f"[Test Case Failure]: {test_data['name']}"
        for issue in existing_issues:
            if issue_title == issue["title"]:
                add_comment_to_issue(
                    issue_number=issue["number"],
                    comment=test_data,
                    repo=test_data["path"].split("/")[1],
                )
                logging.warning("Issue exists!")
                sys.exit()

        issue_title = create_issue(
            issue_data=test_data, repo=test_data["path"].split("/")[1]
        )
