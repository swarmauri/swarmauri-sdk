import json
import sys
from collections import defaultdict


def parse_arguments(args):
    """Parse command-line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze test results from a JSON file."
    )
    parser.add_argument("file", help="Path to the JSON file containing test results")
    parser.add_argument(
        "--required-passed",
        type=str,
        help="Required passed percentage (e.g., 'gt:50', 'lt:30', 'eq:50', 'ge:50', 'le:50')",
    )
    parser.add_argument(
        "--required-skipped",
        type=str,
        help="Required skipped percentage (e.g., 'gt:20', 'lt:50', 'eq:50', 'ge:50', 'le:50')",
    )

    return parser.parse_args(args)


def evaluate_threshold(value, threshold):
    """Evaluate if the value meets the threshold condition."""
    try:
        op, limit = threshold.split(":")
        limit = float(limit)
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
                f"Invalid operator '{op}'. Use 'gt', 'lt', 'eq', 'ge', or 'le'."
            )
    except ValueError as e:
        raise ValueError(
            f"Invalid threshold format '{threshold}'. Expected format: 'gt:<number>', 'lt:<number>', 'eq:<number>', 'ge:<number>', or 'le:<number>'"
        ) from e


def analyze_tags_from_file(file_path, required_passed=None, required_skipped=None):
    try:
        # Load JSON data from the file
        with open(file_path, "r") as f:
            data = json.load(f)

        # Extract the summary and list of tests
        summary = data.get("summary", {})
        tests = data.get("tests", [])

        # Check if the summary and tests exist
        if not summary or not tests:
            print("No test data or summary found in the provided file.")
            return

        # Get total number of tests
        total_tests = summary.get("total", 0)

        # Print summary with percentage
        print("\nTest Results Summary:")
        print(f"{'Category':<15} {'Count':<10} {'Total':<10} {'% of Total':<10}")
        print("-" * 50)
        for category in ["passed", "skipped", "failed"]:
            count = summary.get(category, 0)
            percentage = (count / total_tests) * 100 if total_tests > 0 else 0
            print(
                f"{category.capitalize():<15} {count:<10} {total_tests:<10} {percentage:<10.2f}"
            )

        # Check thresholds
        passed_percentage = (
            (summary.get("passed", 0) / total_tests) * 100 if total_tests > 0 else 0
        )
        skipped_percentage = (
            (summary.get("skipped", 0) / total_tests) * 100 if total_tests > 0 else 0
        )

        threshold_error = False
        if required_passed and not evaluate_threshold(
            passed_percentage, required_passed
        ):
            print(
                f"\nWARNING: Passed percentage ({passed_percentage:.2f}%) does not meet the condition '{required_passed}'!"
            )
            threshold_error = True
        if required_skipped and not evaluate_threshold(
            skipped_percentage, required_skipped
        ):
            print(
                f"WARNING: Skipped percentage ({skipped_percentage:.2f}%) does not meet the condition '{required_skipped}'!"
            )
            threshold_error = True

        print("\n")

        # Group tests by tags
        tag_outcomes = defaultdict(
            lambda: {"passed": 0, "skipped": 0, "failed": 0, "total": 0}
        )

        for test in tests:
            outcome = test["outcome"]
            for tag in test["keywords"]:
                # Exclusion criteria for tags
                if (
                    tag == "tests"  # Exclude tag "tests"
                    or tag.startswith("test_")  # Exclude tags starting with "test_"
                    or tag.endswith("_test.py")  # Exclude tags ending with "_test.py"
                    or tag == ""  # Exclude empty tags
                ):
                    continue
                tag_outcomes[tag]["total"] += 1
                if outcome == "passed":
                    tag_outcomes[tag]["passed"] += 1
                elif outcome == "skipped":
                    tag_outcomes[tag]["skipped"] += 1
                elif outcome == "failed":
                    tag_outcomes[tag]["failed"] += 1

        # Print detailed results by tags
        print("Tag-Based Results:")
        print(
            f"{'Tag':<30} {'Passed':<10} {'Skipped':<10} {'Failed':<10} {'Total':<10} {'% Passed':<10} {'% Skipped':<10} {'% Failed':<10}"
        )
        print("-" * 110)

        # Sort tags by % Passed (descending) and then alphabetically by tag
        sorted_tags = sorted(
            tag_outcomes.items(),
            key=lambda item: (
                -(
                    item[1]["passed"] / item[1]["total"] * 100
                    if item[1]["total"] > 0
                    else 0
                ),  # Sort by % Passed (descending)
                item[0],  # Then by tag (alphabetically)
            ),
        )

        for tag, outcomes in sorted_tags:
            passed = outcomes["passed"]
            skipped = outcomes["skipped"]
            failed = outcomes["failed"]
            total = outcomes["total"]
            passed_percentage = (passed / total) * 100 if total > 0 else 0
            skipped_percentage = (skipped / total) * 100 if total > 0 else 0
            failed_percentage = (failed / total) * 100 if total > 0 else 0
            print(
                f"{tag:<30} {passed:<10} {skipped:<10} {failed:<10} {total:<10} {passed_percentage:<10.2f} {skipped_percentage:<10.2f} {failed_percentage:<10.2f}"
            )

        # Exit with error code if thresholds are not met
        if threshold_error:
            sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from file: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments(sys.argv[1:])

    # Run the analysis
    analyze_tags_from_file(
        file_path=args.file,
        required_passed=args.required_passed,
        required_skipped=args.required_skipped,
    )
