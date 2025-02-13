#!/usr/bin/env python3
"""
test_ops.py

Provides functions to analyze test result data from a JSON file.

The JSON file is expected to have:
  - A "summary" section with keys: "total", "passed", "failed", "skipped".
  - A "tests" list, where each test contains an "outcome" (e.g., "passed", "failed", "skipped")
    and a "keywords" list for tags.

The module:
  - Reads the JSON file.
  - Prints a summary table with counts and percentages.
  - Groups tests by tags (excluding unwanted tags such as "tests", tags starting with "test_", tags
    ending with "_test.py", or empty tags).
  - Checks threshold conditions for passed and skipped percentages (if provided) and exits with an error
    code if the conditions are not satisfied.
"""

import json
import sys
import argparse


def parse_arguments(args):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze test results from a JSON file."
    )
    parser.add_argument("file", help="Path to the JSON file containing test results")
    parser.add_argument(
        "--required-passed",
        type=str,
        help=(
            "Required passed percentage threshold (e.g., 'gt:50', 'lt:30', 'eq:50', "
            "'ge:50', 'le:50')"
        ),
    )
    parser.add_argument(
        "--required-skipped",
        type=str,
        help=(
            "Required skipped percentage threshold (e.g., 'gt:20', 'lt:50', 'eq:50', "
            "'ge:50', 'le:50')"
        ),
    )
    return parser.parse_args(args)


def evaluate_threshold(value, threshold):
    """
    Evaluate if the given value meets the specified threshold condition.

    The threshold format should be: operator:limit (e.g., "gt:50").
    Supported operators:
      - gt: greater than
      - lt: less than
      - eq: equal to
      - ge: greater than or equal to
      - le: less than or equal to

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    try:
        op, limit = threshold.split(":")
        limit = float(limit)
    except ValueError as e:
        raise ValueError(
            f"Invalid threshold format '{threshold}'. Expected format: 'gt:<number>' etc."
        ) from e

    if op == "gt":
        return value > limit
    elif op == "lt":
        return value < limit
    elif op == "eq":
        return value == limit
    elif op == "ge":
        return value >= limit
    elif op == "le":
        return value <= limit
    else:
        raise ValueError(
            f"Invalid operator '{op}'. Use one of: 'gt', 'lt', 'eq', 'ge', 'le'."
        )


def analyze_test_file(file_path, required_passed=None, required_skipped=None):
    """
    Analyzes a JSON file with test results.

    The function:
      - Prints a summary table with the total count and percentage for each outcome.
      - Checks if the percentage of passed or skipped tests meet the specified thresholds.
      - Groups tests by tags (excluding tags that are deemed irrelevant).
      - Prints detailed tag-based results.

    If thresholds are not met, the function exits with an error.

    Args:
        file_path (str): Path to the JSON file.
        required_passed (str, optional): Threshold for passed tests (e.g., "gt:50").
        required_skipped (str, optional): Threshold for skipped tests (e.g., "lt:20").
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading {file_path}: {e}")
        sys.exit(1)

    summary = data.get("summary", {})
    tests = data.get("tests", [])
    if not summary or not tests:
        print("No test data or summary found in the provided file.")
        sys.exit(1)

    total_tests = summary.get("total", 0)
    print("\nTest Results Summary:")
    print(f"{'Category':<15}{'Count':<10}{'Total':<10}{'% of Total':<10}")
    print("-" * 50)
    for category in ["passed", "skipped", "failed"]:
        count = summary.get(category, 0)
        percentage = (count / total_tests) * 100 if total_tests > 0 else 0
        print(
            f"{category.capitalize():<15}{count:<10}{total_tests:<10}{percentage:<10.2f}"
        )

    # Calculate percentages for threshold evaluation.
    passed_pct = (
        (summary.get("passed", 0) / total_tests) * 100 if total_tests > 0 else 0
    )
    skipped_pct = (
        (summary.get("skipped", 0) / total_tests) * 100 if total_tests > 0 else 0
    )

    threshold_error = False
    if required_passed and not evaluate_threshold(passed_pct, required_passed):
        print(
            f"\nWARNING: Passed percentage ({passed_pct:.2f}%) does not meet the condition '{required_passed}'!"
        )
        threshold_error = True

    if required_skipped and not evaluate_threshold(skipped_pct, required_skipped):
        print(
            f"WARNING: Skipped percentage ({skipped_pct:.2f}%) does not meet the condition '{required_skipped}'!"
        )
        threshold_error = True

    # Group tests by tags.
    tag_outcomes = {}
    for test in tests:
        outcome = test.get("outcome", "").lower()
        for tag in test.get("keywords", []):
            # Exclude unwanted tags.
            if (
                tag == "tests"
                or tag.startswith("test_")
                or tag.endswith("_test.py")
                or tag.strip() == ""
            ):
                continue
            if tag not in tag_outcomes:
                tag_outcomes[tag] = {"passed": 0, "skipped": 0, "failed": 0, "total": 0}
            tag_outcomes[tag]["total"] += 1
            if outcome == "passed":
                tag_outcomes[tag]["passed"] += 1
            elif outcome == "skipped":
                tag_outcomes[tag]["skipped"] += 1
            elif outcome == "failed":
                tag_outcomes[tag]["failed"] += 1

    print("\nTag-Based Results:")
    header = f"{'Tag':<30}{'Passed':<10}{'Skipped':<10}{'Failed':<10}{'Total':<10}{'% Passed':<10}{'% Skipped':<10}{'% Failed':<10}"
    print(header)
    print("-" * len(header))
    # Sort tags by percentage passed descending then alphabetically.
    sorted_tags = sorted(
        tag_outcomes.items(),
        key=lambda item: (
            -(
                item[1]["passed"] / item[1]["total"] * 100
                if item[1]["total"] > 0
                else 0
            ),
            item[0],
        ),
    )
    for tag, outcomes in sorted_tags:
        total = outcomes["total"]
        passed_pct = (outcomes["passed"] / total * 100) if total > 0 else 0
        skipped_pct = (outcomes["skipped"] / total * 100) if total > 0 else 0
        failed_pct = (outcomes["failed"] / total * 100) if total > 0 else 0
        print(
            f"{tag:<30}{outcomes['passed']:<10}{outcomes['skipped']:<10}{outcomes['failed']:<10}"
            f"{total:<10}{passed_pct:<10.2f}{skipped_pct:<10.2f}{failed_pct:<10.2f}"
        )

    # If thresholds are not met, exit with a non-zero status code.
    if threshold_error:
        sys.exit(1)
    else:
        print("\nTest analysis completed successfully.")


def main():
    args = parse_arguments(sys.argv[1:])
    analyze_test_file(
        file_path=args.file,
        required_passed=args.required_passed,
        required_skipped=args.required_skipped,
    )


if __name__ == "__main__":
    main()
