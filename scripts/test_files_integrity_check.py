import os
import ast
import logging


# Define color codes
class LogColors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


class CustomFormatter(logging.Formatter):
    def format(self, record):
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

missing_tests = []


def get_classes_from_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def check_files_integrity(path):
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


def validate_test_file(test_file_path, file_path):
    if not os.path.exists(test_file_path):
        missing_tests.append(f"Missing test file for {file_path}")
        logger.error(f"Missing test file for {file_path}")
        raise FileNotFoundError(f"Missing test file for {file_path}")
    logger.info(f"Test file {test_file_path} exists for {file_path}")
    return True


def check_subdir_files(subdir_path, tests_root):
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
