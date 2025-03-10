"""
This script checks if the test files are present for each python file in the given path.
If the test file is missing or empty, it raises an error.
"""

import os
import logging
from typing import List


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

missing_tests: List[str] = []


def check_files_integrity(path: str) -> None:
    """
    Check if the test files are present for each python file in the given path.
    """
    for root, dirs, files in os.walk(path):
        if "tests" not in dirs:
            continue

        for subdir in dirs:
            if subdir == "tests":
                continue

            subdir_path = os.path.join(root, subdir)
            check_subdir_files(subdir_path, os.path.join(root, "tests"))

    if missing_tests:
        logger.info(
            "\n\n==========================Summary of missing test files:===================================\n"
        )
        for missing_test in missing_tests:
            logger.error(missing_test)
        raise RuntimeError("Some test files are missing. Check the logs for details.")
    else:
        logger.info("All test files are present.")


def validate_test_file(test_file_path: str, file_path: str) -> bool:
    """
    Validate the test file for the given python file.
    """
    if not os.path.exists(test_file_path):
        missing_tests.append(f"Missing test file for {file_path}")
        logger.error(f"Missing test file for {file_path}")
        raise FileNotFoundError(f"Missing test file for {file_path}")

    if os.path.getsize(test_file_path) == 0:
        missing_tests.append(f"Test file {test_file_path} is empty for {file_path}")
        logger.error(f"Test file {test_file_path} is empty for {file_path}")
        raise ValueError(f"Test file {test_file_path} is empty for {file_path}")

    logger.info(f"Test file {test_file_path} exists and is not empty for {file_path}")
    return True


def check_subdir_files(subdir_path: str, tests_root: str) -> None:
    """
    Check the files in the given subdirectory.
    """
    for file in os.listdir(subdir_path):
        if file.endswith(".py") and file != "__init__.py":
            file_path = os.path.join(subdir_path, file)
            for root, _, test_files in os.walk(tests_root):
                for test_file in test_files:
                    if file.split(".")[0].lower() in test_file.lower():
                        test_file_path = os.path.join(root, test_file)
                        try:
                            validate_test_file(test_file_path, file_path)
                        except FileNotFoundError:
                            continue
                        break
                else:
                    continue
                break
            else:
                missing_tests.append(f"Missing test file for {file_path}")
                logger.error(f"Missing test file for {file_path}")


if __name__ == "__main__":
    check_files_integrity("pkgs")
